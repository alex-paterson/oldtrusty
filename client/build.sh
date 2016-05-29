#! /bin/bash

javac -cp ".:argparse4j-0.7.0.jar" oldtrustyclient/*.java
jar cmvf META-INF/MANIFEST.MF oldTrustyClient.jar oldtrustyclient/*.class
