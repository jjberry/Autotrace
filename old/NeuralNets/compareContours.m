function [cdist1, cdist2] = compareContours(predictx, predicty, labelx, labely)
% make an image of interpolated contours

  % Interpolate the labeled curve to individual pixels
  lxi = [min(labelx):max(labelx)];
  try
    lyi = interp1(double(labelx),double(labely),lxi,'linear');
  catch
    lyi = interp1(double(labelx)+0.001*rand(size(labelx))-(0.001/2),double(labely),lxi,'linear');    
  end
  % Interpolate the predicted curve to individual pixels
  pxi = [min(predictx):max(predictx)];
  try
    pyi = interp1(double(predictx),double(predicty),pxi,'linear');
  catch
    pyi = interp1(double(predictx)+0.001*rand(size(predictx))-(0.001/2),double(predicty),pxi,'linear');
  end
  
  % get the interpoint distances
  f = zeros(length(pxi), length(lxi));  
  for i = 1:length(pxi)
      for j = 1:length(lxi)
          f(i, j) = sqrt((pxi(i)-lxi(j))^2 + (pyi(i)-lyi(j))^2);
      end
  end

  % Get rid of weird things
  mf = min(f);
  f = f(:,find(~isnan(mf) & ~isinf(mf)));
  
  % Find the closest points to the beginning and end of prediction
  % Don't penalize prediction for going way beyond label.
  [d, minind] = min(f(1,:));
  [d, maxind] = min(f(end,:));

  % The above might not be a good idea, so uncomment lines below to disable trimming the curves
  % minind = 1;
  % maxind = size(f,2);
  
  % Compute average distance from end to end
  minf = min(f(:,minind:maxind));
  cdist1 = mean(minf);

  [d, minind] = min(f(:,1));
  [d, maxind] = min(f(:,end));
  minf = min(f(minind:maxind,:),[],2);
  cdist2 = mean(minf);
  
  % Originally used earth mover's distance, but the above is close enough.
  %[f, fval] = emd([predictx; predicty']', [labelx; labely]',...
  %   1/length(predictx)*ones(length(predictx),1),...
  %   1/length(labelx)*ones(length(labelx),1), @gdf)
 