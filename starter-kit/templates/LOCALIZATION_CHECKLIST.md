# Unicode / Localization Checklist

## User data

- [ ] Unicode file/folder names
- [ ] Cyrillic/non-Latin comp/layer/item names
- [ ] Spaces and special characters
- [ ] Long paths where supported

## Locale

- [ ] Decimal separator differences
- [ ] Thousands separator assumptions
- [ ] Date/time formatting if user-visible
- [ ] Localized AE UI does not break logic
- [ ] Code does not parse localized menu/UI labels when stable IDs/APIs exist

## UI

- [ ] Long translated strings do not clip
- [ ] Resize/layout remains usable
- [ ] Missing translation has defined fallback
- [ ] Declared languages tested in key workflows

## Adobe legacy APIs

- [ ] Encoding of legacy A_char / fixed buffers verified where non-ASCII text is used
- [ ] UTF-8 is not assumed unless the API guarantees it

## Platforms

- [ ] macOS path behavior covered
- [ ] Windows path behavior covered where supported
