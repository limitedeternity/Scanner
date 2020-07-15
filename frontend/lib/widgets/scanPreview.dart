import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_gallery_saver/image_gallery_saver.dart';
import 'package:photo_view/photo_view.dart';

class ScanPreview extends StatefulWidget {
  ScanPreview({this.scan});
  final Uint8List scan;

  @override
  ScanPreviewState createState() => ScanPreviewState();
}

class ScanPreviewState extends State<ScanPreview> {
  bool saving = false;

  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: <Widget>[
          Container(
            height: MediaQuery.of(context).size.height,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                SafeArea(
                  child: Container(
                    padding: EdgeInsets.fromLTRB(20.0, 5.0, 20.0, 5.0),
                    decoration: BoxDecoration(
                      color: Colors.teal,
                      boxShadow: <BoxShadow>[
                        BoxShadow(
                          color: Colors.black12,
                          spreadRadius: 10.0,
                          blurRadius: 20.0,
                        ),
                      ],
                    ),
                    child: Row(
                      children: <Widget>[
                        Container(
                          child: IconButton(
                            icon: IconTheme.merge(
                              data: Theme.of(context).primaryIconTheme,
                              child: Icon(Icons.chevron_left),
                            ),
                            onPressed: () {
                              Navigator.pop(context);
                            },
                            padding: EdgeInsets.zero,
                          ),
                        ),
                        Expanded(
                          child: Text(
                            "Preview",
                            style: Theme.of(context).primaryTextTheme.headline6,
                          ),
                        ),
                        Container(
                          child: IconButton(
                            icon: IconTheme.merge(
                              data: Theme.of(context).primaryIconTheme,
                              child: Icon(Icons.save_alt),
                            ),
                            onPressed: () async {
                              setState(() {
                                saving = true;
                              });

                              await ImageGallerySaver.saveImage(widget.scan);

                              setState(() {
                                saving = false;
                              });

                              HapticFeedback.vibrate();
                              Navigator.pop(context);
                            },
                            padding: EdgeInsets.zero,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                Flexible(
                  flex: 1,
                  child: ClipRect(
                    child: PhotoView(
                      imageProvider: MemoryImage(widget.scan),
                    ),
                  ),
                ),
              ],
            ),
          ),
          saving
              ? Opacity(
                  opacity: 0.5,
                  child: Container(
                    color: Colors.black,
                    child: Center(
                      child: Align(
                        alignment: Alignment.center,
                        child: Text(
                          "Saving...",
                          style: TextStyle(color: Colors.grey, fontSize: 30.0),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                  ),
                )
              : SizedBox.shrink(),
        ],
      ),
    );
  }
}
