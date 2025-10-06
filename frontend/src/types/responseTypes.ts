export type GeneralResponse = {
  status: number;
  detail: string;
};

export type GeneralDataResponse = GeneralResponse & {
  data: any;
};
