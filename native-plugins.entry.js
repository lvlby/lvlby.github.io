// Bundled by the GitHub workflow into www/native-plugins.js (Android app only; the website never loads it).
// index.html finds the plugins on window.LvNative (see nplug() in index.html).
import { FirebaseAuthentication } from '@capacitor-firebase/authentication';
import { LocalNotifications } from '@capacitor/local-notifications';
import { Filesystem } from '@capacitor/filesystem';
import { Share } from '@capacitor/share';

window.LvNative = { FirebaseAuthentication, LocalNotifications, Filesystem, Share };
