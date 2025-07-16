# Installing Webfonts
Follow these simple Steps.

## 1.
Put `technor/` Folder into a Folder called `fonts/`.

## 2.
Put `technor.css` into your `css/` Folder.

## 3. (Optional)
You may adapt the `url('path')` in `technor.css` depends on your Website Filesystem.

## 4.
Import `technor.css` at the top of you main Stylesheet.

```
@import url('technor.css');
```

## 5.
You are now ready to use the following Rules in your CSS to specify each Font Style:
```
font-family: Technor-Extralight;
font-family: Technor-Light;
font-family: Technor-Regular;
font-family: Technor-Medium;
font-family: Technor-Semibold;
font-family: Technor-Bold;
font-family: Technor-Black;
font-family: Technor-Variable;

```
## 6. (Optional)
Use `font-variation-settings` rule to controll axes of variable fonts:
wght 900.0

Available axes:
'wght' (range from 200.0 to 900.0

