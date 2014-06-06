# This document takes in two groups of ultrasound traces and runs SSANOVA on them.  


######## SS ANOVA CODE FROM THE LAB WEBSITE #########
######## Copy this into the R terminal and press enter. ########

################################################################
# function codes -- sort of like m-files.  we just have to put
# this in once

# comp will give you the smoothing spline fit
# to get smoothing parameter values, type summary(*)

comp<-function(data,word1,word2){
#       w1w2<-data[data$word == word1 | data$word == word2,]
	w1w2<-rbind(subset(data,word == word1),subset(data,word == word2));

       a<-levels(w1w2$word)
       word3<-a[a!=word1 & a!=word2]
       levels(w1w2$word)<-list(word1=c(word1,word3),word2=word2)
       fit.w1w2<-ssr(Y~word*X,rk=list(cubic(X),rk.prod(cubic(X),shrink1(word))),
               data=w1w2,scale=T)
}

#comp.plot will you the fitted curves and corresponding BCI's

comp.plot<-function(fit,word.1,word.2){
       w1<-fit$data[fit$data$word=="word1",]
       w2<-fit$data[fit$data$word=="word2",]
       n1<-nrow(w1)
       ntot<-nrow(w1)+nrow(w2)
       fit.pred<-predict(fit)
       fit.w1<-data.frame(fit=fit.pred$fit[1:n1],pstd=fit.pred$pstd[1:n1])
       fit.w2<-data.frame(fit=fit.pred$fit[n1+1:ntot],pstd=fit.pred$pstd[n1+1:ntot])
       order1<-order(w1$X)
       order2<-order(w2$X)
       par(mfrow=c(1,1))
       plot(fit$data$X,-fit$data$Y,type="n",xlab="X",ylab="Y")
       #points(w1$X,-w1$Y,col=2,pch=".")
       lines(w1$X[order1],-fit.w1$fit[order1],col=2,lwd=5)
       lines(w1$X[order1],-fit.w1$fit[order1]+3*fit.w1$pstd[order1],col=2,lwd=1,lty=3)
       lines(w1$X[order1],-fit.w1$fit[order1]-3*fit.w1$pstd[order1],col=2,lwd=1,lty=3)
       #points(w2$X,-w2$Y,col=3,pch=".")
       lines(w2$X[order2],-fit.w2$fit[order2],col=3,lwd=5)
       lines(w2$X[order2],-fit.w2$fit[order2]+3*fit.w2$pstd[order2],col=3,lwd=1,lty=3)
       lines(w2$X[order2],-fit.w2$fit[order2]-3*fit.w2$pstd[order2],col=3,lwd=1,lty=3)
       title(paste(word.1,"vs",word.2))

	coords <- par("usr");
	legend(coords[1]+5,coords[4]-5,c(word.1,word.2),lwd=5,col=c(2,3))
}

# Same as comp.plot2 above, but uses point markers that will show up in grayscale


comp.plot2<-function(fit,word.1,word.2){
       w1<-fit$data[fit$data$word=="word1",]
       w2<-fit$data[fit$data$word=="word2",]
       n1<-nrow(w1)
       ntot<-nrow(w1)+nrow(w2)
       fit.pred<-predict(fit)
       fit.w1<-data.frame(fit=fit.pred$fit[1:n1],pstd=fit.pred$pstd[1:n1])
       fit.w2<-data.frame(fit=fit.pred$fit[n1+1:ntot],pstd=fit.pred$pstd[n1+1:ntot])
       order1<-order(w1$X)
       order2<-order(w2$X)
       par(mfrow=c(1,1))
       plot(fit$data$X,-fit$data$Y,type="n",xlab="X",ylab="Y")

       lines(w1$X[order1],-fit.w1$fit[order1],col=1,lwd=5)
       lines(w1$X[order1],-fit.w1$fit[order1]+3*fit.w1$pstd[order1],col=1,lwd=1,lty=3)
       lines(w1$X[order1],-fit.w1$fit[order1]-3*fit.w1$pstd[order1],col=1,lwd=1,lty=3)

       lines(w2$X[order2],-fit.w2$fit[order2],col=3,lwd=5)
       lines(w2$X[order2],-fit.w2$fit[order2]+3*fit.w2$pstd[order2],col=3,lwd=1,lty=3)
       lines(w2$X[order2],-fit.w2$fit[order2]-3*fit.w2$pstd[order2],col=3,lwd=1,lty=3)
       title(paste(word.1,"vs",word.2))

	coords <- par("usr");
	legend(coords[1]+5,coords[4]-5,c(word.1,word.2),lwd=5,col=c(1,3))
}

#getting Bayes Confidence Intervals for interaction effects
#if the BCI's include 0 at a given value of X, then the two curves are
#similar there.

get.int<-function(fit,word.1,word.2){
       w1<-fit$data[fit$data$word=="word1",]
       w2<-fit$data[fit$data$word=="word2",]
       n1<-nrow(w1)
       ntot<-nrow(w1)+nrow(w2)
       fit.pred<-predict(fit,terms=c(0,1,0,1,0,1))
       fit.w1<-data.frame(fit=fit.pred$fit[1:n1],pstd=fit.pred$pstd[1:n1])
       fit.w2<-data.frame(fit=fit.pred$fit[n1+1:ntot],pstd=fit.pred$pstd[n1+1:ntot])
       order1<-order(w1$X)
       order2<-order(w2$X)
       par(mfrow=c(2,1))
       ylimits<-c(min(-fit.w1$fit[order1]-3*fit.w1$pstd[order1]),
               max(-fit.w1$fit[order1]+3*fit.w1$pstd[order1]))
       plot(fit$data$X,-fit.pred$fit,type="n",xlab="X",ylab="Y",ylim=ylimits)
       abline(0,0)
       lines(w1$X[order1],-fit.w1$fit[order1],col=2,lwd=5)
       lines(w1$X[order1],-fit.w1$fit[order1]+3*fit.w1$pstd[order1],col=2,lwd=1,lty=3)
       lines(w1$X[order1],-fit.w1$fit[order1]-3*fit.w1$pstd[order1],col=2,lwd=1,lty=3)
       title(paste("Interaction effects w/BCI for",word.1))
       ylimits<-c(min(-fit.w2$fit[order2]-3*fit.w2$pstd[order2]),
               max(-fit.w2$fit[order2]+3*fit.w2$pstd[order2]))
       plot(fit$data$X,-fit.pred$fit,type="n",xlab="X",ylab="Y",ylim=ylimits)
       abline(0,0)
       lines(w2$X[order2],-fit.w2$fit[order2],col=3,lwd=5)
       lines(w2$X[order2],-fit.w2$fit[order2]+3*fit.w2$pstd[order2],col=3,lwd=1,lty=3)
       lines(w2$X[order2],-fit.w2$fit[order2]-3*fit.w2$pstd[order2],col=3,lwd=1,lty=3)
       title(paste("Interaction effects w/BCI for",word.2))
       list(get.int=fit.pred)
}

compare<-function(w1,w2,data){
	sepsp.t1<-comp(data=data,w1,w2)
	summary(sepsp.t1)
	comp.plot(sepsp.t1,w1,w2)
#	interaction.bci<-get.int(sepsp.t1,w1,w2)
}

comparegray<-function(w1,w2,data){
	sepsp.t1<-comp(data=data,w1,w2)
	summary(sepsp.t1)
	comp.plot2(sepsp.t1,w1,w2)
#	interaction.bci<-get.int(sepsp.t1,w1,w2)
}

##################################################################
# for ssatest.txt
##################################################################

library(assist)
options(memory=1000000000)

########## THE CODE FROM THE WEBSITE ENDS HERE ###################







##### Now, fill in the location of the data file below.  Then, copy
##### all of the code below into the R terminal and press enter.


datalocation <- '/Users/apiladmin/Desktop/GaelicEpenthesisHC/GaelicS8/GaelicS8_SSANOVAfile3.txt'

mydata <- read.table(datalocation,h=T)


##### Finally, call on the SSANOVA code.  You will need to change to words below to each
##### of the Gaelic words in turn.  After you produce a graph, make sure to save it before 
##### producing the next one.

compare("airgeadV1", "airgeadV2", mydata);  # Make sure to save the graph!
 