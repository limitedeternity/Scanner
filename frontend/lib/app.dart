import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:image_picker/image_picker.dart';
import 'package:dio/dio.dart';
import 'package:scanner/core/queryPermissions.dart';
import 'package:scanner/core/findScanServer.dart';
import 'package:scanner/widgets/scanPreview.dart';

class Application extends StatefulWidget {
  @override
  ApplicationState createState() => ApplicationState();
}

class ApplicationState extends State<Application> {
  bool permissionsGranted = false;
  String scanServerAddress = null;
  bool scanInProgress = false;
  bool getFromCamera = true;

  final _scaffoldKey = GlobalKey<ScaffoldState>();

  Future<File> getImage() async {
    final pickedImage = await ImagePicker().getImage(
      source: getFromCamera ? ImageSource.camera : ImageSource.gallery,
    );
    return pickedImage != null ? File(pickedImage.path) : null;
  }

  @override
  void initState() {
    super.initState();

    queryPermissions().then((void _) {
      setState(() {
        permissionsGranted = true;
      });
    });

    findScanServer().then((String ipaddr) {
      setState(() {
        scanServerAddress = ipaddr;
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      appBar: AppBar(
        title: Text("Scanner"),
      ),
      body: Center(
        child: Align(
          alignment: Alignment.center,
          child: Text(
            !permissionsGranted
                ? "Required permissions weren't granted"
                : scanServerAddress == null
                    ? "Searching for scan server..."
                    : scanInProgress
                        ? "Scanning..."
                        : "Select image by pressing button below",
            style: TextStyle(
              color: Colors.grey,
              fontSize: 20.0,
            ),
            textAlign: TextAlign.center,
          ),
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
      floatingActionButton: !permissionsGranted
          ? FloatingActionButton(
              onPressed: () {
                _scaffoldKey.currentState.showSnackBar(
                  SnackBar(
                    content: Text(
                      "Wanna grant permissions after all these years?",
                    ),
                    action: SnackBarAction(
                      label: "Always",
                      onPressed: openAppSettings,
                    ),
                  ),
                );
              },
              child: Container(
                child: CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              ),
            )
          : scanServerAddress == null
              ? FloatingActionButton(
                  onPressed: () {
                    _scaffoldKey.currentState.showSnackBar(
                      SnackBar(
                        content: Text(
                          "Better check if the server is up and running",
                        ),
                      ),
                    );
                  },
                  child: Container(
                    child: CircularProgressIndicator(
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  ),
                )
              : scanInProgress
                  ? FloatingActionButton(
                      onPressed: () {
                        _scaffoldKey.currentState.showSnackBar(
                          SnackBar(
                            content: Text(
                              "Please be patient",
                            ),
                          ),
                        );
                      },
                      child: Container(
                        child: CircularProgressIndicator(
                          valueColor:
                              AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      ),
                    )
                  : InkWell(
                      customBorder: CircleBorder(),
                      onLongPress: () {
                        setState(() {
                          getFromCamera = !getFromCamera;
                        });
                        HapticFeedback.vibrate();
                      },
                      child: FloatingActionButton(
                        onPressed: () async {
                          File image = await getImage();
                          if (image == null) {
                            return;
                          }

                          int size = await image.length();

                          setState(() {
                            scanInProgress = true;
                          });

                          try {
                            final response = await Dio().post(
                              "http://$scanServerAddress:8080/scan",
                              data: image.openRead(),
                              options: Options(
                                headers: {
                                  Headers.contentLengthHeader: size,
                                },
                                responseType: ResponseType.bytes,
                              ),
                            );

                            Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (BuildContext context) {
                                  return ScanPreview(
                                    scan: Uint8List.fromList(response.data),
                                  );
                                },
                              ),
                            ).then((dynamic _) {
                              setState(() {
                                scanInProgress = false;
                              });
                            });
                          } on DioError catch (e) {
                            setState(() {
                              scanInProgress = false;
                              scanServerAddress = null;
                            });

                            findScanServer().then((String ipaddr) {
                              setState(() {
                                scanServerAddress = ipaddr;
                              });
                            });
                          }
                        },
                        child: getFromCamera
                            ? Icon(Icons.camera_alt)
                            : Icon(Icons.collections),
                      ),
                    ),
    );
  }
}
