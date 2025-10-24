export default function Button({text, link, state, onClick}) {
  return(
    <a>
      <button onClick={onClick}>{text}</button>
    </a>
  );
}