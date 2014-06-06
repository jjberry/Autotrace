% First case is a regression problem. Fit the curve.
if 1
    data = getPRMLdata('curve');
    label = data(:,end) * 2;
    data = data(:,1:end-1);
    nnet.normalization_type = 'mean_and_var';
    [data, nnet] = normalizedata(data, nnet, nnet.normalization_type);

    sample = false; % Decide to sample or not when pretraining
    max_iter_rbm = 100; % Number of iterations during pretraining each layer
    layer_size = [size(data,2), 5, 2, 30, 1]; % nnet structure
    layer_type = {'gaussian', 'sigmoid', 'gaussian', 'sigmoid', 'gaussian'};

    % Train in unsupervised mode
    disp(['Layer sizes: ', sprintf('%9d ', layer_size)]);
    disp(['Layer types: ', sprintf('%9.9s ', layer_type{:})]);
    disp(' ');

    no_hidden_layers = length(layer_size)-1;
    network = cell(1, no_hidden_layers);
    
    % Learn layer-by-layer to get an initial network configuration
    [nnet.network] = train_deep_network(data, layer_size, layer_type, 'Extern', [], [], [], sample, max_iter_rbm, 0);

    network = backprop(nnet.network, data, label, 30, 'linSquaredErr',[],[], 'reconstruction' );
    %network = lbfgsNN(nnet.network, data, label, 100, 'linSquaredErr')
    
    figure(1)
    plot(data,label, 'rx')
    hold on
    xi = linspace(min(data), max(data), 100)';
    yi = run_through_network(network,xi);
    plot(xi, yi, 'b-')
    hold off
else
    data = getPRMLdata('gaussians');
    label = data(:,end);
    data = data(:,1:end-1);
    nnet.normalization_type = 'mean_and_var';
    [data, nnet] = normalizedata(data, nnet, nnet.normalization_type);
    
    classes = unique(label);
    targets = zeros(size(data,1), length(classes));
    for i = 1:length(classes)
        inds = find(label == classes(i));
        targets(inds,i) = 1;
    end
    sample = false; % Decide to sample or not when pretraining
    max_iter_rbm = 100; % Number of iterations during pretraining each layer
    layer_size = [size(data,2), 5, 20, 5, length(classes)]; % nnet structure
    layer_type = {'gaussian', 'sigmoid', 'gaussian', 'sigmoid', 'exp'};

    % Train in unsupervised mode
    disp(['Layer sizes: ', sprintf('%9d ', layer_size)]);
    disp(['Layer types: ', sprintf('%9.9s ', layer_type{:})]);
    disp(' ');

    no_hidden_layers = length(layer_size)-1;
    network = cell(1, no_hidden_layers);
    % Learn layer-by-layer to get an initial network configuration
    [nnet.network] = train_deep_network(data, layer_size, layer_type, 'Extern', [], [], [], sample, max_iter_rbm, 0);
    % network = backprop(nnet.network, data, targets, 20, 'softMax', [], [], 'classification' );
    network = lbfgsNN(nnet.network, data, targets, 100, 'softMax')

    [xi, yi] = meshgrid([min(data(:,1))-nnet.std/2:.05:max(data(:,1))+nnet.std/2], ...
                        [min(data(:,2))-nnet.std/2:.05:max(data(:,2))+nnet.std/2]);
    result = run_through_network(network,[xi(:), yi(:)]);
    result = exp(result);
    result = result./repmat(sum(result,2), [1,2]);
    pcolor(xi, yi, reshape(result(:,1), size(xi)))
    shading('interp')
    colormap('pink')
    hold on
    [c,h] = contour(xi,yi,reshape(result(:,1),size(xi)),[0.5, 0.5]);
    set(get(h,'Children'),'EdgeColor','black')
    c = 'rb';
    for i = 1:length(classes)
        inds = find(label == classes(i));
        plot(data(inds,1), data(inds, 2), [c(i), 'x'])        
    end
    hold off
end
