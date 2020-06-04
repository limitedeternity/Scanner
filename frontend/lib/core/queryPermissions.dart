import 'package:permission_handler/permission_handler.dart';

Future<void> queryPermissions() async {
  List<Permission> perms = [Permission.storage, Permission.camera];

  while (true) {
    Map<Permission, PermissionStatus> statuses = await perms.request();

    bool allGranted = statuses.values
        .every((PermissionStatus status) => status == PermissionStatus.granted);

    if (allGranted) {
      break;
    }

    await Future.delayed(Duration(milliseconds: 300));
  }
}
