function [result, smallcx, smallcy, largecx, largecy] = reconstructContours(datadir, i, subjid, contnetwork, XC, contfiles, cxc, cyc, height, width, continds, m, s, interprows, interpcols, minx, miny, show, usepolar)
  if ~exist('show') || isempty(show)
    show = true;
  end
  if ~exist('usepolar') || isempty(usepolar)
    usepolar = true;
  end
  

  % Ultrasound to Contour result
  cind = [1:length(continds)] + height*width;

  tic
  % Get an image representation of the network prediction
  result = run_through_network(contnetwork, XC(i,1:height*width));
  img = zeros(height,width);
  img(continds) = result(1:length(continds)).*s(cind) + m(cind);
  contresult = img;
  
  % Extract a smooth tongue contour out of the image
  if (usepolar) 
    [smallcx, smallcy] = contourFromPolar(img);
  else
    [smallcx, smallcy] = contourFromImg(img);
  end
  largecx = (smallcx-.5)*interpcols/width+minx-1;
  largecy = (smallcy-.5)*interprows/height+miny-1;  
  toc
  if show
    % Show the contour in small aspect
    figure(3)
    % do some thresholding
    imgm = mean(img(:));
    imgs = std(img(:));
    img(img<(imgm)) = imgm;
    img = img-imgm;
    imshowtrue(img);
    hold on
    plot(smallcx,smallcy,'g-',(cxc{i}-minx+1)*width/interpcols+.5,(cyc{i}-miny+1)*height/interprows+.5,'r-')
    hold off

    % Show the contour on top of the original image
    figure(4)
    filename = fullfile(datadir,['Subject' num2str(subjid(i))], 'IMAGES',contfiles{i});
    img = imread( filename );
    subplot(2,1,1)
    imshowtrue(img);
    subplot(2,1,2)
    imshowtrue(img);
    hold on
    %plot(largecx, largecy, 'g-', cxc{i}+.5, cyc{i}+.5, 'r-')
    plot(largecx, largecy, 'g-');
    hold off
  end
  
function [newx, newy] = contourFromPolar(img)
  % Convert to polar coordinates
  origin = [round(size(img,2)/2), -round(size(img,1)*1.2)];  % in x, y coords, down is negative
  anglestep = -pi/100;
  angles = [pi:anglestep:0];
  maxr = size(img,1)*2;
  rstep = maxr/100;
  radiuses = [0:rstep:maxr];
  clear xi yi pimg
  for a = 1:length(angles)
    for r = 1:length(radiuses)
      [x,y] = pol2cart(angles(a), radiuses(r));
      xi(a,r) = x + origin(1);
      yi(a,r) = y + origin(2);
    end
  end
  [x,y] = meshgrid([1:size(img,2)],[-1:-1:-(size(img,1))]);
  pimg = interp2(x,y,img,xi,yi)';
  pimg(isnan(pimg)) = min(min(img));
  %imshowtrue(pimg)

  % Extract a smooth tongue contour out of the polar image
  temp = 0.05;
  [vals, inds] = max(pimg);
  [pheight, pwidth] = size(pimg);
  inds = [1:pheight]*exp(pimg/temp) ./ sum(exp(pimg/temp));
  h = 2; kern = [0, 0];
  smallcx = find(vals>0.3);
  smallcx = [min(smallcx):max(smallcx)];
  f = getBinSmoothHandle(h,smallcx,kern);  % Precompute everything not data-driven
  smallcy = f(inds(smallcx)-pheight)+pheight;

  % convert back to x,y coordinates
  clear newx newy
  for i = 1:length(smallcx)
    [x,y] = pol2cart(angles(smallcx(i)), (smallcy(i)-1)*rstep);
    newx(i) = origin(1) + x;
    newy(i) = -(origin(2) + y);
  end
  %imshowtrue(img)
  %hold on
  %plot(newx+.5, newy+.5,'r-')
  %hold off

function [smallcx, smallcy] = contourFromImg(contresult)
  % Extract a smooth tongue contour out of the image
  [vals, inds] = max(contresult);
  temp = 0.05;
  inds = [1:height]*exp(contresult/temp) ./ sum(exp(contresult/temp));
  h = 1; kern = [0, 0];
  smallcx = find(vals>0.3);
  smallcx = [min(smallcx):max(smallcx)];
  f = getBinSmoothHandle(h,smallcx,kern);  % Precompute everything not data-driven
  smallcy = f(inds(smallcx)-height)+height;

  
