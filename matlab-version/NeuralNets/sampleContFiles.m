function [contfiles, id, contx, conty] = samplecontfiles(contfiles, id, contx, conty, max_num_images)

  numconts = length(contfiles);
  if max_num_images < numconts
    rp = randperm(numconts);
    contx = contx(rp(1:max_num_images),:);
    conty = conty(rp(1:max_num_images),:);
    contfiles = contfiles(rp(1:max_num_images));
    id = id(rp(1:max_num_images));
  end


