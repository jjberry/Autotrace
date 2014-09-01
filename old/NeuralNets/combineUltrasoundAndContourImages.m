function [XC, m, s, height, width, continds] = combineUltrasoundAndContourImages(contfiles, id, contimgs, datadir, roi)

  top = roi(1);
  bottom = roi(2);
  left = roi(3);
  right = roi(4)

  directory = fullfile(datadir,['Subject' num2str(id(1))], 'IMAGES')
  % Read one image to see what the final size will be when we resize it
  scale = 0.1;
  img = imread( fullfile(directory, contfiles{1}) );

  % test to see whether or not image is grayscale
  if size(img, 3) == 3
    img = rgb2gray(img(top:bottom,left:right,:));
  end
  cropped = double(imresize(img, scale,'bicubic'));
  [height, width] = size(cropped);

  % Set things up to remove the always zero elements from the contours
  continds = [];
  numconts = length(contfiles);
  for i = 1:numconts
    cont = imresize(contimgs{i},[height,width],'bicubic');
    continds = unique(cat(1,continds, find(cont > 0.01)));
  end


  % Load the images, crop, resize, and concatenate the contour data
  XC = zeros(numconts,height*width + length(continds));
  for j = 1:numconts
      % For all images with a contour, load and crop and grayscale the image
      directory = fullfile(datadir,['Subject' num2str(id(j))], 'IMAGES');
      img = imread( fullfile(directory,contfiles{j}) );

      % test to see whether or not image is grayscale
      if size(img, 3) == 3
        img = rgb2gray(img(top:bottom,left:right,:));
      end
      cropped = double(imresize(img,scale,'bicubic'));

      % subplot(3,1,1)
      % imshowtrue(cropped);

      % Scale and concatenate the contour data
      cont = imresize(contimgs{j},[height,width],'bicubic');

      % subplot(3,1,2)
      % imshowtrue(cont);

      s = max(cont);
      s(s<0.01) = 1;
      cont = cont ./ repmat(s,[height,1]);
      cont(cont<0) = 0;

      % subplot(3,1,3)
      % imshowtrue(cont);
      % pause

      XC(j,:) = [cropped(:)', cont(continds)'];
  end

  % Normalize
  m = mean(XC);
  s = std(XC);
  s(s < 0.001) = 1;
  XC = (XC-repmat(m,[numconts,1]))./repmat(s,[numconts,1]);
