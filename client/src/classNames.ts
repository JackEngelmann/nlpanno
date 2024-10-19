export function classNames(...classNames: (string | undefined | boolean)[]) {
  return classNames.filter((cn) => Boolean(cn)).join(" ");
}
