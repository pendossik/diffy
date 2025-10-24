import './index.css';
import Records from './records.json';

export default function Search({text, value, onChange}) {
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