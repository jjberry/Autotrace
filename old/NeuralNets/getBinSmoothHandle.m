function handle = getBinSmoothHandle(h,x,kern)
% GETBINSMOOTHHANDLE  Get handle to a smoothed, piecewise-linear function estimator
% handle = getBinSmthHandle(h,x,kern) returns a handle to a function
% yhat = handle(y) which estimates a smoothed function at points x by applying local 
% linear regression to data y, using abscissa x, bandwidth h and kernel kern.  This 
% function precomputes all values that do not depend on data and returns a handle
% to a function that needs data, in order to speed up the case where there are many 
% different functions which have the same abscissa, kernel, outpoints, and bandwidth, 
% but with different outputs 'y' which you want to compute repeatedly.
% 
% Input arguments are:
% If kern=0, uses Gaussian kernel.  If kern=1, uses 1/(1+x^2).  If kern=2 
% uses Epanechnikov kernel 0.75*(1-x^2) on [-1<x<1]. If kern=3, uses square function.
% If kern has two elements, and the second element is 1, then the estimate is 
% done using Naradaya-Watson kernel density estimate, instead of LLR.  In practice
% this results in a slight speedup at the cost of greater bias at the edges.
% 
% Example:
% x = [1:90];
% h = 2; kern = [0, 1];
% f = getBinSmoothHandle(h,x,kern)  % Precompute everything not data-driven
% for i = 1:10
%   y = sin( (x+randn(size(x))*2)/7.5 );  % generate Gaussian noise corrupted sine
%   yhat = f(y);    % Compute the estimated function
%   plot(x,y,'b+', x, yhat, 'r-')
%   pause
% end

  zerotol=1e-14;
  z = x;
  if length(kern)==2 && kern(2)==1
    kernelDensityOnly = true;
  else
    kernelDensityOnly = false;
  end

  kern = kern(1);
  % reshape takes almost no cycles
  x = reshape(x,[length(x),1]); z = reshape(z,[length(z),1]);

  [xx,zz] = meshgrid(x,z);
  difs = xx-zz;
  kernvals = g(difs/h,kern);
  s0 = sum(kernvals,2);
  
  if kernelDensityOnly  % Just find weighted mean, ignore slope
    s0_inv = 1./(s0 + zerotol);
    handle = @kernelDensityEstimation;
  else % Otherwise, compute s1, s2, and t1 to get offset and slope for local linear fit
    difskern = difs.*kernvals;
    s1 = sum(difskern,2);
    temp = difs.*difskern;
    s2 = sum(temp,2);
    s0_s2_minus_s1_s1_inv = 1 ./ ((s0.*s2 - s1.*s1)+zerotol);
    handle = @localLinearRegression;
  end

  function yhat = kernelDensityEstimation(y)
    y = reshape(y,[length(y),1]); 
    t0 = kernvals*y;
    yhat = t0.*s0_inv;  
  end

  function yhat = localLinearRegression(y)
    y = reshape(y,[length(y),1]); 
    t0 = kernvals*y;
    t1 = difskern*y;
    % Add zerotol to avoid divide by zero on flat series.
    % yhat = (s2.*t0 - s1.*t1) ./ (s0*s2 - s1*s1 + zerotol);
    yhat = (s2.*t0 - s1.*t1) .* s0_s2_minus_s1_s1_inv;
  end
  
end

% Kernel evaluating subfunction.
function gx = g(x,kern)
  switch(kern)
   case 0
    % Uses normal curve with s=1, mu=0.
    gx = exp(-((x.*x)/2)) ; % Use x.*x not x.^2 for speed.
   case 1   
    % Uses 1/(1+x^2) kernel.
    gx = 1./(1+(x.*x));
   case 2
    % Uses Epanechnikov kernel. Doesn't bother to use MEXed Fortran
    % code; didn't turn out much quicker than (vectorised) Matlab!
    gx = max(0.75*(1-x.*x),0);
   case 3
    gx = double(logical(abs(x)<=0.5));
  end
end