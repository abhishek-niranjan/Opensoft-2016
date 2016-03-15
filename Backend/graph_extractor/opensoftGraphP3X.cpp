#include "opencv2/core/core.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <sys/socket.h> // For the socket (), bind () etc. functions.
#include <netinet/in.h> // For IPv4 data struct..
#include <string.h> // For memset.
#include <arpa/inet.h> // For inet_pton (), inet_ntop ().
#include <bits/stdc++.h>

using namespace std;
using namespace cv;

int main(int argc, char ** argv){
    int minx,miny,maxy,maxx;
    Mat I = imread("graph_0.jpg", CV_LOAD_IMAGE_GRAYSCALE);
    FILE *f=fopen("graph_0.txt","r");
    fscanf(f,"%d %d %d %d",&minx,&miny,&maxx,&maxy);

    cv:: Rect myRect(minx-10.0,maxy-30.0,(maxx-minx)+60.0,20);
    cv::Mat imagecropped=I(myRect);
    string name="graph_axes_0.jpg";

    I = imagecropped;
    imshow(name,I);
    waitKey(0);
    imwrite("graph0_fftx.jpg",I);

    return 0;
}