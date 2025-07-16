# Installing Webfonts
Follow these simple Steps.

## 1.
Put `khand/` Folder into a Folder called `fonts/`.

## 2.
Put `khand.css` into your `css/` Folder.

## 3. (Optional)
You may adapt the `url('path')` in `khand.css` depends on your Website Filesystem.

## 4.
Import `khand.css` at the top of you main Stylesheet.

```
@import url('khand.css');
```

## 5.
You are now ready to use the following Rules in your CSS to specify each Font Style:
```
font-family: Khand-Light;
font-family: Khand-Regular;
font-family: Khand-Medium;
font-family: Khand-SemiBold;
font-family: Khand-Bold;
font-family: Khand-Variable;

```
## 6. (Optional)
Use `font-variation-settings` rule to controll axes of variable fonts:
wght 300.0

Available axes:
'wght' (range from 300.0 to 700.0

