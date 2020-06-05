# Scanner
> Top-tier OpenCV document scanner with Flutter frontend

## Main points

* There are two parts: frontend (Flutter GUI) and backend (Flask Server).

* This application works only within one network.

* Backend does all the image processing and is required to be up and running.

## Setup

### Backend (on your computer)

1. Fetch `backend` from [Releases](https://github.com/limitedeternity/Scanner/releases).

2. Install [Python 3.7](https://wiki.python.org/moin/BeginnersGuide/Download).

3. Upgrade `pip`: `pip3 install --user --upgrade pip`

4. Pull `libmagic`:
  * [Windows x64](https://github.com/pidydx/libmagicwin64)
  * Debian/Ubuntu: `sudo apt-get install libmagic1`
  * Mac: `brew install libmagic`
 
5. Install `make`:
  * Windows x64:
     * [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
     * [Make](http://gnuwin32.sourceforge.net/packages/make.htm)
  * Debian/Ubuntu: `sudo apt-get install build-essential`
  * Mac: `xcode-select --install`
 
6. Go to `backend` folder, open a console there and run `make install`
  
### Frontend (on your phone)

1. Fetch `app-*-release.apk` from [Releases](https://github.com/limitedeternity/Scanner/releases) (where `*` is your processor architecture) and [install it](https://www.androidpit.com/android-for-beginners-what-is-an-apk-file).

## Usage

1. Start the backend with `make run`.

2. Start the frontend. The application will request **STORAGE** and **CAMERA** permissions on the first run – grant them. The frontend will connect to the backend in ~3s (if not already).

3. You'll see a button at the bottom of the screen. Tap it to take a photo with your camera. Alternatively, you can long-press this button and it'll allow you to select a photo from the gallery (an icon on the button will change).

4. After you've taken a photo, the application will send it to the backend and wait for it to respond with a scanned variant. Result will be shown in a "Preview" window.

5. You can discard a result by tapping the left button on the top bar (or going back) or save it to the gallery by tapping the right button on the top bar.

## Screenshots

### Main screen

![Screenshot_20200604-135405](https://user-images.githubusercontent.com/24318966/83752646-8ae4ff00-a671-11ea-91f2-5b837b48a2d4.png)

### Test sample

![receipt](https://user-images.githubusercontent.com/24318966/83752695-a0f2bf80-a671-11ea-80c8-4c4ea85aaf5a.jpg)

### Preview

![Screenshot_20200604-135400](https://user-images.githubusercontent.com/24318966/83752741-b1a33580-a671-11ea-94f6-3c6acd0f5c7b.png)


## Meta

Distributed under the GPL-3.0 license. See ``LICENSE`` for more information.

[@limitedeternity](https://github.com/limitedeternity)
