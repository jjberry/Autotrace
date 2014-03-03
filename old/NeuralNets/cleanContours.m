function [cxc, cyc, minx, maxx, miny, maxy] = cleanContours(contx, conty)

numconts = size(contx,1);

minxs = [];
maxxs = [];
minys = [];
maxys = [];
for i = 1:numconts
  % Get the valid x and y values of the contours, and sort the x-axis
  cx = contx(i,:); cx = cx(cx>0);
  cy = conty(i,:); cy = cy(cy>0);
  [cx, inds] = sort(cx);
  cy = cy(inds);

  % Collect min and max
  minxs = [minxs,min(cx)];
  maxxs = [maxxs,max(cx)];
  minys = [minys,min(cy)];
  maxys = [maxys,max(cy)];

  % For some reason there are X,Y pairs with the same X.  So this is a simple fix.
  nz = min([10, floor(length(cx)/3)]);
  for j = 1:nz
    ind = find(cx(1:nz)==cx(j));
    if length(ind) > 1
      cy(ind) = sort(cy(ind),'descend');
      cx(ind) = linspace(cx(j)-.5,cx(j)+.5,length(ind));
    end
  end
  for j = 1:nz
    ind = find(cx(end-nz+1:end)==cx(end-nz+j));
    if length(ind) > 1
      cy(end-nz+ind) = sort(cy(end-nz+ind),'ascend');
      cx(end-nz+ind) = linspace(cx(end-nz+j)-.5,cx(end-nz+j)+.5,length(ind));
    end
  end

  cxc{i} = cx;
  cyc{i} = cy;
%  plot(cx,cy,'rx',xi,yic(i,:),'b-')
%  axis([250 600 140 340])
%  pause
end

% Pick min and max to restrict to the midldle 98% of data
minxs = sort(minxs); minx = minxs(1); %minxs(floor(length(minxs)*.01));
maxxs = sort(maxxs); maxx = maxxs(end-floor(length(maxxs)*.01));
minys = sort(minys); miny = minys(1); % floor(length(minys)*.01));
maxys = sort(maxys); maxy = maxys(end-floor(length(maxys)*.01));

