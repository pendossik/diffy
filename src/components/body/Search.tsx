import Records from '../../records.json';

type Props = {
  text: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}
export default function Search({text, value, onChange}: Props) {

  return(
    <div>
    <input placeholder={text} value={value} onChange={onChange} list='items'></input>
    <datalist id='items'>
      <option>{Records[0].name}</option>
      <option>{Records[1].name}</option>
      <option>{Records[2].name}</option>
    </datalist>
    </div>
  );
}