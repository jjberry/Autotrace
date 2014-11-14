function [contimgs, interprows, interpcols] = makeContourImages(cxc, cyc, minx, maxx, miny, maxy)
% make an image of interpolated contours

  interprows = maxy-miny+1;
  interpcols = maxx-minx+1;
  h = interprows/100;
  for i = 1:length(cxc)
    contimg = zeros(interprows,interpcols);
    cx = cxc{i};
    cy = cyc{i};
    
    yi = dointerp('linear');
    yi2 = dointerp('spline');
    xd = max(cx)-min(cx);
    if xd > 6;
      ind = [floor(.1*xd):ceil(.9*xd)];
      yi(ind) = yi2(ind);
    end
      
    
    
    for j = 1:length(yi)
      if ~isnan(yi(j)) && (j+minx-1 >= min(cx)) && (j+minx-1 <= max(cx)) 
        for k = 1:interprows
          contimg(k,j) = exp( -(((miny+k-1) - yi(j))/h)^2);
        end
      end
    end
    %imshowtrue(contimg)
    %drawnow
    %pause
    contimgs{i} = contimg./(max(max(contimg)));
    %if i == 82
    %  keyboard
    %end
  end
  
  function yi = dointerp(interp_type)
    try
      yi = interp1(double(cx),double(cy),[minx:maxx],interp_type);
    catch
      yi = interp1(double(cx+rand(size(cx))*0.001),double(cy),[minx:maxx],interp_type);
    end
  end
  
end