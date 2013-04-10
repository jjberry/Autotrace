#include <stdlib.h>
#include <stdio.h>
#include <math.h>

int main(int argc, char *argv[])
{
	FILE *in, *out, *settings;
	char *filebase = (char*)malloc(50);
	char *infile = (char*)malloc(50);
	char *outfile = (char*)malloc(50);
	char *fn = (char*)malloc(200);
	short ct;
	short ulx,uly,urx,ury,llx,lly,lrx,lry,tmp;
	short OverlayX, OverlayY;
	double Angle, UsScale,tranlrmm,ortranrmm,ortranlmm;
	short XOffset, YOffset;
	double AngleOffset;
	short i, nread, len;
	double X, Y, tmpX, tmpY;

	char *token = (char*)malloc(200);
	char *item = (char*)malloc(200);
	char *tabdelimited = (char*)malloc(1);

	short *x = (short*)malloc(sizeof(short)*32);
	short *y = (short*)malloc(sizeof(short)*32);
	short *pt = (short*)malloc(sizeof(short)*8);
	short *ax = (short*)malloc(sizeof(short)*10);
	short *ay = (short*)malloc(sizeof(short)*10);

	settings = fopen("settings.txt","r");
	if(settings==NULL) { printf("Couldn\'t open settings.txt\n"); return -1; }

	if(fscanf(settings,"OverlayX = %hd\n",&OverlayX)==0) { printf("Error reading value of: OverlayX\n"); return -1; }
	if(fscanf(settings,"OverlayY = %hd\n",&OverlayY)==0) { printf("Error reading value of: OverlayY\n"); return -1; }
	if(fscanf(settings,"Angle = %lf\n",&Angle)==0) { printf("Error reading value of: Angle\n"); return -1; }
	if(fscanf(settings,"UsScale = %lf\n",&UsScale)==0) { printf("Error reading value of: UsScale\n"); return -1; }
	if(fscanf(settings,"distance_btwn_lower_dots = %lf\n",&tranlrmm)==0) { printf("Error reading value of: distance_btwn_lower_dots\n"); return -1; }
	if(fscanf(settings,"tip_of_transducer_to_lower_right_dot = %lf\n",&ortranrmm)==0) { printf("Error reading value of: tip_of_transducer_to_lower_right_dot\n"); return -1; }
	if(fscanf(settings,"tip_of_transducer_to_lower_left_dot = %lf\n",&ortranlmm)==0) { printf("Error reading value of: tip_of_transducer_to_lower_left_dot\n"); return -1; }
	fclose(settings);

	printf("Using these settings:\n");
	printf("OverlayX = %hd\n",OverlayX);
	printf("OverlayY = %hd\n",OverlayY);
	printf("Angle = %lf\n",Angle);
	printf("UsScale = %lf\n",UsScale);
	printf("distance_btwn_lower_dots = %lf\n",tranlrmm);
	printf("tip_of_transducer_to_lower_right_dot = %lf\n",ortranrmm);
	printf("tip_of_transducer_to_lower_left_dot = %lf\n",ortranlmm);
	printf("\n");

	if(argc < 2)
	{
		printf("Enter the filename (without \'.txt\'): ");
		scanf("%s",filebase);
	}
	else
	{
		strcpy(filebase,argv[1]);
	}
	if(argc < 3)
	{
		printf("Would you like tab-delimited format instead of R/SSANOVA format? (y/n)\n");
		scanf("%s",tabdelimited);
	}
	else
	{
		*tabdelimited = *argv[2];
	}
	strcpy(infile,filebase);
	strcat(infile,".txt");
	strcpy(outfile,filebase);
	strcat(outfile,"_output.txt");

//	printf("%s\n%s\n",infile,outfile);

	in = fopen(infile,"r");
	if(in==NULL)
	{
		printf("Unable to open file: %s\n",infile);
		return -1;
	}
	out = fopen(outfile,"w");
	if(out==NULL)
	{
		printf("Unable to open file: %s\n",outfile);
		return -1;
	}

	fscanf(in,"Filename Raw.R1.X Raw.R1.Y Raw.R2.X Raw.R2.Y Raw.R3.X Raw.R3.Y Raw.R4.X Raw.R4.Y Raw.R5.X Raw.R5.Y Raw.R6.X Raw.R6.Y Raw.R7.X Raw.R7.Y Raw.R8.X Raw.R8.Y Raw.R9.X Raw.R9.Y Raw.R10.X Raw.R10.Y Raw.R11.X Raw.R11.Y Raw.R12.X Raw.R12.Y Raw.R13.X Raw.R13.Y Raw.R14.X Raw.R14.Y Raw.R15.X Raw.R15.Y Raw.R16.X Raw.R16.Y Raw.R17.X Raw.R17.Y Raw.R18.X Raw.R18.Y Raw.R19.X Raw.R19.Y Raw.R20.X Raw.R20.Y Raw.R21.X Raw.R21.Y Raw.R22.X Raw.R22.Y Raw.R23.X Raw.R23.Y Raw.R24.X Raw.R24.Y Raw.R25.X Raw.R25.Y Raw.R26.X Raw.R26.Y Raw.R27.X Raw.R27.Y Raw.R28.X Raw.R28.Y Raw.R29.X Raw.R29.Y Raw.R30.X Raw.R30.Y Raw.R31.X Raw.R31.Y Raw.R32.X Raw.R32.Y UL.x UL.y UR.x UR.y LL.x LL.y LR.x LR.y Aux1.x Aux1.y Aux2.x Aux2.y Aux3.x Aux3.y Aux4.x Aux4.y Aux5.x Aux5.y Aux6.x Aux6.y Aux7.x Aux7.y Aux8.x Aux8.y Aux9.x Aux9.y Aux10.x Aux10.y");

	double orheaddist, orheadangle, vidoriginx, vidoriginy, vidscale, imagecenterx = 360.5, imagecentery = 267.0, tranangle, usoriginx = 390, usoriginy = 416, ortrandist, ortranangle, headangle, htangle, headx, heady, centerheaddist, centerheadangle, rotatedheadx, rotatedheady;

	if(*tabdelimited == 'y')
	{
		fprintf(out,"Filename\t");
		for(i=0; i<32; i++)
		{
			fprintf(out,"x.%i\ty.%i\t",i+1,i+1);
		}
		for(i=0; i<10; i++)
		{
			fprintf(out,"aux.x.%i\taux.y.%i\t",i+1,i+1);
		}
		fprintf(out,"\n");
	}
	else
	{
		fprintf(out,"word\ttoken\tX\tY\n");
	}

	while(0==feof(in))
	{
		nread = fscanf(in,"%s\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\n",fn,x,y,x+1,y+1,x+2,y+2,x+3,y+3,x+4,y+4,x+5,y+5,x+6,y+6,x+7,y+7,x+8,y+8,x+9,y+9,x+10,y+10,x+11,y+11,x+12,y+12,x+13,y+13,x+14,y+14,x+15,y+15,x+16,y+16,x+17,y+17,x+18,y+18,x+19,y+19,x+20,y+20,x+21,y+21,x+22,y+22,x+23,y+23,x+24,y+24,x+25,y+25,x+26,y+26,x+27,y+27,x+28,y+28,x+29,y+29,x+30,y+30,x+31,y+31,pt,pt+1,pt+2,pt+3,pt+4,pt+5,pt+6,pt+7,ax,ay,ax+1,ay+1,ax+2,ay+2,ax+3,ay+3,ax+4,ay+4,ax+5,ay+5,ax+6,ay+6,ax+7,ay+7,ax+8,ay+8,ax+9,ay+9);

		if(nread!=93)
		{
			printf("\nFor the entry \"%s\", only %d items were read, whereas I was expecting 93. I\'m going to skip that line and finish the rest of the file.\n\n",fn,nread);
			continue;
		}

		ulx = *(pt+0);
		uly = *(pt+1) * ((double)533/(double)480);
		urx = *(pt+2);
		ury = *(pt+3) * ((double)533/(double)480);
		llx = *(pt+4);
		lly = *(pt+5) * ((double)533/(double)480);
		lrx = *(pt+6);
		lry = *(pt+7) * ((double)533/(double)480);

		// for checking that the input has been read correctly
		// note that the video points' y-coordinates have already been stretched
/*		printf("%hd %hd\n%hd %hd\n%hd %hd\n%hd %hd\n\n",ulx,uly,urx,ury,llx,lly,lrx,lry);
		for(i=0;i<10;i++)
		{
			printf("%hd\t%hd\n",*(ax+i),*(ay+i));
		}
*/
		vidscale = tranlrmm/sqrt(  (lrx-llx)*(lrx-llx) + (lly-lry)*(lly-lry));
		ortrandist = ortranlmm / vidscale;
		ortranangle = atan(-1.0f*ortranrmm*sin(acos( (tranlrmm*tranlrmm + ortranrmm*ortranrmm - ortranlmm*ortranlmm) / (2.0f * tranlrmm * ortranrmm))) / (tranlrmm - ortranrmm * cos(acos(( tranlrmm*tranlrmm + ortranrmm*ortranrmm - ortranlmm*ortranlmm) / (2 * tranlrmm * ortranrmm)))));

		tranangle = atan((double)(lly - lry)/(double)(lrx - llx));
		headangle = atan((double)(uly - ury)/(double)(urx - ulx));
		htangle = headangle - tranangle;
		AngleOffset = htangle - Angle*(-3.1415926535897932384626433832795/180.0f);

		vidoriginx = llx - (ortrandist * cos(ortranangle - tranangle));
		vidoriginy = lly - (ortrandist * sin(ortranangle - tranangle));

		orheaddist = vidscale/UsScale * sqrt((ulx - vidoriginx)*(ulx - vidoriginx) + (uly - vidoriginy)*(uly - vidoriginy));
		orheadangle = acos((ulx - vidoriginx)/(sqrt( (ulx - vidoriginx)*(ulx - vidoriginx) + (vidoriginy - uly)*(vidoriginy - uly) ))) - tranangle;

		headx = usoriginx + orheaddist * cos(orheadangle);
		heady = usoriginy - orheaddist * sin(orheadangle);

		centerheaddist = sqrt( (headx - imagecenterx)*(headx - imagecenterx) + (imagecentery - heady)*(imagecentery - heady));
		centerheadangle = atan((headx - imagecenterx)/(imagecentery - heady));

		rotatedheadx = imagecenterx + (centerheaddist * sin(centerheadangle + AngleOffset));
		rotatedheady = imagecentery - (centerheaddist * cos(centerheadangle + AngleOffset));

		XOffset = (short)(OverlayX - rotatedheadx);
		YOffset = (short)(OverlayY - rotatedheady);

		// for checking the Palatron calculations
/*
		printf("vidoriginx: %lf\n",vidoriginx);
		printf("vidoriginy: %lf\n",vidoriginy);
		printf("rotatedheadx: %lf\n",rotatedheadx);
		printf("rotatedheady: %lf\n",rotatedheady);
		printf("vidscale: %lf\n",vidscale);
		printf("ortrandist: %lf\n",ortrandist);
		printf("ortranangle: %lf\n",ortranangle);
		printf("tranangle: %lf\n",tranangle);

		printf("%hd\t%hd\t%lf\n",XOffset,YOffset,AngleOffset);
*/
		// negative because Jeff's code outputs a clockwise rotation
		AngleOffset *= -1;

		// For the aux points
		for(i=0;i<32;i++)
		{
			X = (double)*(x + i);
			Y = (double)*(y + i);


			if(X!=-1)
			{
				Y *= (double)533/(double)480;

				// rotate first
				// bring it back to the origin
				X -= 360;
				Y -= 266.5;

				// rotate it about the origin
				tmpX = X*cos(AngleOffset) + Y*sin(AngleOffset);
				tmpY = Y*cos(AngleOffset) - X*sin(AngleOffset);

				// send it back to image-centered space
				X = tmpX + 360;
				Y = tmpY + 266.5;

				// do the translation as well
				X += XOffset;
				Y += YOffset;

				*(x + i) = (int)X;
				*(y + i) = (int)Y;
			}
			else
			{
				*(x + i) = -1;
				*(y + i) = -1;
			}

		}
//		return -1;

		// Now for the aux points
		// redefine AngleOffset -- headangle minus the "clamped" angle
		AngleOffset = headangle - Angle*(-3.1415926535897932384626433832795/180.0f);
		AngleOffset *= -1;

		// refine the X and Y offsets
		XOffset = OverlayX - ulx;
		YOffset = OverlayY - uly;

//		printf("%lf\n",headangle);
//		printf("%hd\t%hd\t%lf\n",XOffset,YOffset,AngleOffset);
		for(i=0;i<10;i++)
		{
			X = (double)*(ax + i);
			Y = (double)*(ay + i);

			if(X!=-1)
			{
				Y *= (double)533/(double)480;

				// rotate first
				// bring it back to the origin
				X -= 360;
				Y -= 266.5;

				// rotate it about the origin
				tmpX = X*cos(AngleOffset) + Y*sin(AngleOffset);
				tmpY = Y*cos(AngleOffset) - X*sin(AngleOffset);

				// send it back to image-centered space
				X = tmpX + 360;
				Y = tmpY + 266.5;

				// do the translation as well
				X += XOffset;
				Y += YOffset;

				*(ax + i) = (int)X;
				*(ay + i) = (int)Y;
			}
			else
			{
				*(ax + i) = -1;
				*(ay + i) = -1;
			}

		}


		if(*tabdelimited == 'y')
		{
			fprintf(out,"%s\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\t%hd\n",fn,*(x),*(y),*(x+1),*(y+1),*(x+2),*(y+2),*(x+3),*(y+3),*(x+4),*(y+4),*(x+5),*(y+5),*(x+6),*(y+6),*(x+7),*(y+7),*(x+8),*(y+8),*(x+9),*(y+9),*(x+10),*(y+10),*(x+11),*(y+11),*(x+12),*(y+12),*(x+13),*(y+13),*(x+14),*(y+14),*(x+15),*(y+15),*(x+16),*(y+16),*(x+17),*(y+17),*(x+18),*(y+18),*(x+19),*(y+19),*(x+20),*(y+20),*(x+21),*(y+21),*(x+22),*(y+22),*(x+23),*(y+23),*(x+24),*(y+24),*(x+25),*(y+25),*(x+26),*(y+26),*(x+27),*(y+27),*(x+28),*(y+28),*(x+29),*(y+29),*(x+30),*(y+30),*(x+31),*(y+31),*(ax),*(ay),*(ax+1),*(ay+1),*(ax+2),*(ay+2),*(ax+3),*(ay+3),*(ax+4),*(ay+4),*(ax+5),*(ay+5),*(ax+6),*(ay+6),*(ax+7),*(ay+7),*(ax+8),*(ay+8),*(ax+9),*(ay+9));
		}
		else
		{
			len = strpbrk(fn,"1234567890")-fn;
			strncpy(token,fn,len);
			*(token + len) = '\0';
			len = strchr(fn,'_')-strpbrk(fn,"1234567890");
			strncpy(item,strpbrk(fn,"1234567890"),len);
			*(item + len) = '\0';

			for(i=0; i<32; i++)
			{
				if(*(x+i) != -1)
				{
					fprintf(out,"%s\t%s\t%hd\t%hd\n",token,item,*(x+i),*(y+i));
				}
			}
		}

	}

	fclose(in);
	fclose(out);
}
