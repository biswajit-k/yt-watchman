export function hovered(classes) {
  const classList = classes.split(" ").map((className) => "hover:" + className);
  console.log(classList.join(" "));
  return classList.join(" ");
}
