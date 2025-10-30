export default function Button({text, link, state, onClick}) {
  return(
    <a>
      <button className="comparison-form__compare-button" onClick={onClick}>{text}</button>
    </a>
  );
}