import { v4 } from "uuid";
import DocumentsDb from "./db";
import { DocumentStatusEnum } from "./types/enums";

export default class DocumentsHelper extends DocumentsDb {
  protected getInitialStatus = (): string => {
    return DocumentStatusEnum.UPLOADED;
  };

  protected generateJobUuid = (): string => {
    return v4();
  };
}
