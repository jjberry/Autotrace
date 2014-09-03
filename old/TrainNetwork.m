% TrainNetwork.m
% Written by Jeff Berry on Jul 1 2010
%
% purpose:
%   Train a tDBN to trace tongue contours
%
% usage:
%   See TrainNetwork.py
%
%--------------------------------------------------
% Modified by Jeff Berry on Feb 19 2011
% reason:
%   Added support for scriptable region of interest
%


function TrainNetwork(train_ultrasound, train_contours, test_ultrasound, test_contours, practice_run, max_num_images, use_crossval, Nfolds, network_sizes, network_types, data_dir, subject_nums, roi)
  % Old args from jointUltraContoursDeepnet.m
  % (simpletest, numHidLayers, pretrain, pretrainWithJointContourLabels, autoencoder, Nfolds)
  % Options depending on how much compute power we have

  % We're ignoring user inputs for train, test ultrasound, contours, and assuming
  % train_ultrasound & train_contours = true
  % test_ultrasound = true, test_contours = false
  % i.e. we're training a deep net for autotracing

  numHidLayers = 3;
  pretrain = true;
  pretrainWithJointContourLabels = true;
  autoencoder = true;

  if practice_run
    show = false
    numRBMiter = 40;
    numBPiter = 10;
  else
    show = false
    numRBMiter = 100;
    numBPiter = 30;
  end

  %---------------------------------------
  addpath('NeuralNets');

  NNetMinimization = 'backprop';
  % NNetMinimization = 'lbfgsNN'

  [contfiles, subjectid, contx, conty] = loadContours(data_dir, subject_nums);
  [contfiles, subjectid, contx, conty] = ...
    sampleContFiles(contfiles, subjectid, contx, conty, max_num_images);

  [cxc, cyc, minx, maxx, miny, maxy] = cleanContours(contx, conty);
  %cyc $for debug purposes (finding empty traces, single-point traces, etc)
  [contimgs, interprows, interpcols] = ...
    makeContourImages(cxc, cyc, minx, maxx, miny, maxy);

  %%%% Do the deep net learning of contours %%%%%

  [XC, m, s, height, width, continds] = combineUltrasoundAndContourImages(...
    contfiles, subjectid, contimgs, data_dir, roi);

  clear contimgs

  % Split into N-fold validation sets
  ndata = size(XC,1);
  segs = floor(linspace(1,ndata,Nfolds+1));
  segs(end) = ndata+1;
  rp = randperm(ndata);
  for i = 1:1
    % Separate into current train and validation sets
    validinds = segs(i):(segs(i+1)-1);
    traininds = setdiff([1:ndata],validinds);
    %validinds = [1:ndata];
    %traininds = [1:ndata];

    if pretrainWithJointContourLabels
      trainX = XC(rp(traininds),:);
      trainT = XC(rp(traininds),:);
      validX = XC(rp(validinds),:);
      validT = XC(rp(validinds),:);
    else
      trainX = XC(rp(traininds),1:height*width);
      trainT = XC(rp(traininds),continds);
      validX = XC(rp(validinds),1:height*width);
      validT = XC(rp(validinds),continds);
    end

    layers = eval(network_sizes);
    types = network_types;

    if ~autoencoder
      layers = cat(2,layers, length(continds));
      types = cat(2,types,'gaussian');
    end
    if ~pretrain
      numRBMiter = 0;
    end


    if autoencoder
      % Pre-train the deep net
      deepnet = train_deep_network(trainX, layers, types, 'None', trainT, validX, validT, false, numRBMiter, 1, []);

      % "unroll" the original network to make it an autoencoder
      no_layers = length(deepnet);
      for j=1:no_layers
        deepnet{2 * no_layers + 1 - j} = deepnet{j};
        deepnet{2 * no_layers + 1 - j}.W = deepnet{j}.W';
        deepnet{2 * no_layers + 1 - j}.bias = deepnet{j}.bias_downW';
        deepnet{2 * no_layers + 1 - j}.hidtype = deepnet{j}.vistype;
        deepnet{2 * no_layers + 1 - j}.vistype = deepnet{j}.hidtype;
      end
    else
      % Pre-train the deep net
      deepnet = train_deep_network(trainX, layers, types, 'Extern', trainT, validX, validT, false, numRBMiter, 1, []);
    end
    originalnetwork = deepnet;

    % Done with pre-training for full representation
    % Now convert first layer to code the ultrasound data only

    if pretrainWithJointContourLabels
      % Pull out the first layer
      inputlayernet{1} = deepnet{1};
      hiddenrep = run_through_network(inputlayernet, XC);
      trainH = hiddenrep(rp(traininds),:);
      validH = hiddenrep(rp(validinds),:);

      % New training data only uses ultrasound on the input
      trainX = XC(rp(traininds),1:height*width);
      validX = XC(rp(validinds),1:height*width);

      % Train the RBM on ultrasound only to match the original hidden representation
      fprintf(1, 'Training translational RBM')
      etas = [0.0025, 0.001, 0.0001, 0.000025];
      for j = 1:length(etas)
        [newinputlayer, recon_error] = trainRBM(trainX, 1, trainH, layers(2), types{1}, types{2}, etas(j), 500, false);
        recon_errors(j) = recon_error(2);
        if ~(isinf(recon_errors(j)) || isnan(recon_errors(j)) || mean(recon_error) > 1000)
           break;
        end
      end

      % Drop in the replacement first layer
      do_additional_backprop = true;
      if do_additional_backprop
        % Do additional backprop
        clear contnetwork
        contnetwork{1} = newinputlayer;
        contnetwork{1}.W = newinputlayer.W{1}'; % cell because we are using trainRBM that can do multinomials
        contnetwork{1}.bias = newinputlayer.bias_upW';
        eval(['[contnetwork, trainerr, validerr] = ', NNetMinimization, '(contnetwork, trainX, trainH, numBPiter, ''crossEntropy'', validX, validH, ''reconstruction'', 0, []);']);
        deepnet{1} = contnetwork{1};
      else
        deepnet{1}.W = newinputlayer.W{1}'; % cell because we are using trainRBM that can do multinomials
        deepnet{1}.bias = newinputlayer.bias_upW';
      end

      if autoencoder
        deepnet{end}.W = deepnet{end}.W(height*width+1:end,:);
        deepnet{end}.bias = deepnet{end}.bias(height*width+1:end);
      end
      trainT = XC(rp(traininds),height*width+1:end);
      validT = XC(rp(validinds),height*width+1:end);
    end

    if ~autoencoder
      % Discriminatively train to targets
      deepnet = RidgeLastLayer(deepnet, trainX, trainT, 0.1, [], validX, validT);
      % [contnetwork, trainerr(i), validerr(i)] = backprop(deepnet, trainX, trainT, numBPiter, 'linSquaredErr', validX, validT, 'reconstruction', 0, []);
      eval(['[contnetwork, trainerr(i), validerr(i)] =', ...
            NNetMinimization,'(deepnet, trainX, trainT, numBPiter, ''linSquaredErr'', validX, validT, ''reconstruction'', 0, [])']);
      fprintf(1,'Mean train err: %d, Mean valid err: %d\n', mean(trainerr),mean(validerr));
    else
      % Train with gradient method to make ultrasound inputs produce only the contour output
      eval(['[contnetwork, trainerr, validerr] =', NNetMinimization, '(deepnet, trainX, trainT, numBPiter, ''linSquaredErr'', validX, validT, ''reconstruction'', 0, []);']);
    end

    % Test goodness
    iind = 1:height*width;
    cind = [1:length(continds)] + height*width;
    vind = rp(validinds);
    %vind = rp(traininds);
    clear cdist1 cdist2
    for jj = 1:length(vind);
      j = vind(jj);
      [img, smallcx, smallcy, largecx, largecy] = reconstructContours(data_dir, j, subjectid, contnetwork, XC, contfiles, cxc, cyc, height, width, continds, m, s, interprows, interpcols, minx, miny, show);
      drawnow
      [cdist1(jj), cdist2(jj)] = compareContours(largecx, largecy, cxc{j}, cyc{j});
    end

    meancdist1(i) = mean(cdist1)
    meancdist2(i) = mean(cdist2)
    meancdist(i) = mean([mean(cdist1), mean(cdist2)])
    fprintf('Saving trained network...')
    save savefiles/network contnetwork originalnetwork continds s m minx maxx miny maxy meancdist
    save savefiles/meancdist meancdist meancdist1 meancdist2
  end
