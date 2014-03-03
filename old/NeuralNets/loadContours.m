function [contfiles, id, contx, conty] = loadContours(datadir, subjectnums)

  contfiles = {};
  contx = [];
  conty = [];
  id = [];
  for i = 1:length(subjectnums)
    filename = fullfile(datadir, ['Subject' num2str(subjectnums(i))], 'TongueContours.csv')  
    % Read contours
    n = 92;
    ds = repmat('%d',[1,n]);
    fid = fopen(filename);
    header = fgetl(fid);
    data = textscan(fid,['%s',ds],'Delimiter','\t','CollectOutput',1);
    contfiles = cat(1,contfiles,data{1});
    id = cat(1,id,repmat(subjectnums(i),[length(data{1}),1]));
    contx = cat(1,contx,double(data{2}(:,1:2:64)));
    conty = cat(1,conty,double(data{2}(:,2:2:64)));
  end
