export function classNames(...classNames: (string | undefined)[]) {
  return classNames.filter((cn) => Boolean(cn)).join(" ");
}
