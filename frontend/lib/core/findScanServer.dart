import 'package:udp/udp.dart';

Future<String> findScanServer() async {
  final reciever = await UDP.bind(Endpoint.any(port: Port(37020)));
  String ipaddr = null;

  await reciever.listen((datagram) {
    final message = String.fromCharCodes(datagram.data);
    if (message == "e9ad115d-388e-4e8e-a630-999832d92217") {
      ipaddr = datagram.address.host;
    }
  });

  while (ipaddr == null) {
    await Future.delayed(Duration(milliseconds: 800));
  }

  reciever.close();
  return ipaddr;
}
