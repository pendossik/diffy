export type Product = {
  id: number;
  name: string;
  img?: string | null;
  characteristics_groups?: CharGroup[];
};

type Char = {
  id: number;
  name: string;
  value: string;
};

type CharGroup = {
  name: string;
  characteristics: Char[];
};