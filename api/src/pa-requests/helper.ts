import PaRequestDb from "./db";
import { PaRequestStatusEnum } from "./types/enums";

export default class PaHelper extends PaRequestDb {
  protected getInitialStatus = (): string => {
    return PaRequestStatusEnum.CREATED;
  };
}
