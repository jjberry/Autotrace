% AutoTracer.m
% Written by Jeff Berry on Aug 5 2010
%
% purpose:
%   use a tDBN <networkfile> to estimate a tongue contour trace for a set of ultrasound images
%
% usage:
%   controlled by AutoTrace.py
%   args: directory, roi, networkfile
%       directory: the location of the images to be traced
%       roi: specifications of the region of interest
%       networkfile: the location of the trained tDBN
%
%--------------------------------------------------
% Modified by Jeff Berry on Feb 25 2011
% reason:
%   changed to add the tracer initials (networkname without the '.mat') to the output filenames
%

function [xs, ys, worst] = AutoTracer(directory, roi, networkfile)
	addpath('NeuralNets/')
	load(networkfile);
	
  %Gus: changed to support multiple image formats
  files = [ dir(fullfile(directory, '*.jpg')) ; dir(fullfile(directory, '*.png'))];
	
	for i = 1:length(files);
		[xs{i}, ys{i}] = TraceOne(fullfile(directory, files(i).name), contnetwork, continds, maxx, minx, maxy, miny, s, m, roi);
		iminds = zeros(length(xs{i}),3);
		iminds(:,2) = xs{i};
		iminds(:,3) = ys{i};
		iminds(:,1) = [1:length(xs{i})];
		[pathjunk, networkname, extjunk] = fileparts(networkfile);
		fname = strcat(files(i).name, '.', networkname, '.traced.txt');
		dlmwrite(fullfile(directory, fname), iminds, 'delimiter', '\t', 'newline', 'unix');
	end

function [largecx, largecy, contresult] = TraceOne(filename, contnetwork, continds, maxx, minx, maxy, miny, s, m, roi)    
    top = roi(1);
    bottom = roi(2);
    left = roi(3);
    right = roi(4);
    
	scale = 0.1;
	 
	%keyboard	
	% Read one image to see what the final size will be when we resize it
	img = imread( filename );
	cropped = double(imresize(rgb2gray(img(top:bottom,left:right,:)),scale,'bicubic'));
	[height, width] = size(cropped);

	XC = cropped(:)';
	XC = (XC-m(1:(height*width)))./s(1:(height*width));
	
	% from reconstructContours.m
	result = run_through_network(contnetwork, XC);
	cind = [1:length(continds)] + height*width;
	contresult = zeros(height,width);
	contresult(continds) = result(1:length(continds)).*s(cind) + m(cind);
	%figure(2)
	%imshow(contresult, [], 'InitialMagnification', 'fit');
	 
	crm = mean(contresult(:));
	crs = std(contresult(:));
	contresult(contresult<(crm)) = crm;
	contresult = contresult-crm;
	contresult = contresult ./ (max(max(contresult)));

	%[smallcx, smallcy] = contourFromImg(contresult);
	[smallcx, smallcy, H] = contourFromPolar(contresult);
	
	interprows = maxy-miny+1;
	interpcols = maxx-minx+1;
	
	largecx = (smallcx-.5)*interpcols/width+minx-1;
	largecy = (smallcy-.5)*interprows/height+miny-1;  

	h = figure(1);
	subplot(2,1,1)
    imshow(img);
    subplot(2,1,2)
    imshow(img);
    hold on
    p = plot(largecx, largecy, 'g-');
	set(p,'LineWidth',1);
    hold off
    %saveas(h, strcat(filename,'traced.jpg'))

function [newx, newy, wiggle] = contourFromPolar(img)
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

  H = 0;
  for i = 1:pwidth
	softcol = exp(pimg(:,i)/temp) ./ sum(exp(pimg(:,i)/temp));
	H = H - softcol'*log(softcol);
  end

  h = 2; kern = [0, 0];
  smallcx = find(vals>0.3);
  smallcx = [min(smallcx):max(smallcx)];
  f = getBinSmoothHandle(h,smallcx,kern);  % Precompute everything not data-driven
  smallcy = f(inds(smallcx)-pheight)+pheight;

  winsize = 5;
  wiggle = 0;
  for p = 1:length(smallcy)-winsize+1
	wiggle = wiggle + std(smallcy(p:p+winsize-1));
  end
  wiggle = wiggle/(length(smallcy)-winsize+1);

  % convert back to x,y coordinates
  clear newx newy
  for i = 1:length(smallcx)
    [x,y] = pol2cart(angles(smallcx(i)), (smallcy(i)-1)*rstep);
    newx(i) = origin(1) + x;
    newy(i) = -(origin(2) + y);
  end

function [smallcx, smallcy] = contourFromImg(contresult)
  % Extract a smooth tongue contour out of the image
  height = 19;
  [vals, inds] = max(contresult);
  temp = 0.05;
  inds = [1:height]*exp(contresult/temp) ./ sum(exp(contresult/temp));
  h = 1; kern = [0, 0];
  smallcx = find(vals>0.3);
  smallcx = [min(smallcx):max(smallcx)];
  f = getBinSmoothHandle(h,smallcx,kern);  % Precompute everything not data-driven
  smallcy = f(inds(smallcx)-height)+height;

   