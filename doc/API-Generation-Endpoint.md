# API Documentation Generation Page

## Endpoints

### 1. GET `/api/generation/filters`
**Возвращает:** `TGenerationFiltersResponse`
```typescript
type TGenerationFiltersResponse = {
  tasks: TFilterConfig;
  models: TFilterConfig;
  domains: TFilterConfig;
};

type TFilterConfig = {
  items: TFilterItem[];
  label: string;
  labelPlacement?: 'top' | 'left';
};

type TFilterItem = {
  id: string;
  label: string;
  value: string;
  default?: boolean;
};
```

---

### 2. GET `/api/generation/form-config?taskId=...&modelId=...&domainId=...`
**Возвращает:** `TDynamicForm`
```typescript
type TDynamicForm = TFormField[];

type TFormField = ITextField | ITextAreaField | IUploadFileField | ISelectField;

interface ITextField {
  type: 'single';
  name: string;
  label: string;
  placeholder?: string;
  labelPlacement?: 'top' | 'left';
  required: boolean;
}

interface ITextAreaField {
  type: 'multiline';
  name: string;
  label: string;
  placeholder?: string;
  labelPlacement?: 'top' | 'left';
  required: boolean;
  size: 's' | 'm' | 'l';
}

interface IUploadFileField {
  type: 'photo';
  name: string;
  label: string;
  labelPlacement?: 'top' | 'left';
  required: boolean;
}

interface ISelectField {
  type: 'select';
  name: string;
  label: string;
  labelPlacement?: 'top' | 'left';
  required: boolean;
  withSearch?: boolean;
  multiple?: boolean;
  items: Array<{id: string, label: string}>
}
```

---

### 3. POST `/api/generation/generate`
**Отправляю:** `TGenerationRequest` (JSON или FormData если есть File)
```typescript
type TGenerationRequest = {
  filters: {
    taskId: string;
    modelId: string;
    domainId: string;
  };
  fields: Array<{
    name: string;
    value: string | string[] | File;
  }>;
};
```

**Примечания:**
- Если `value` является массивом и используется FormData, массив отправляется как JSON строка
- Пример FormData: `fields[0].value = JSON.stringify(['value1', 'value2'])`

**Возвращает:** `TGenerationResponse`
```typescript
type TGenerationResponse = {
  success: boolean;
  data?: TGenerationResult;
  error?: string;
};

type TGenerationResult = {
  html: string;
  text: string;
};
```

---

### 4. POST `/api/generation/generate-excel`
**Отправляю:** `TGenerationExcelRequest` (JSON)
```typescript
type TGenerationExcelRequest = {
  filters: {
    taskId: string;
    modelId: string;
  };
  excelLink: string;
  range: {
    from: number;
    to: number;
  };
};
```

**Примечания:**
- Используется для генерации контента из Excel файла
- Поле `excelLink` содержит ссылку на Excel файл
- Поля `range.from` и `range.to` указывают диапазон строк для обработки (0 означает отсутствие ограничения)
- Фильтр `domainId` не требуется для Excel генерации

**Возвращает:** `TGenerationResponse`
```typescript
type TGenerationResponse = {
  success: boolean;
  data?: TGenerationResult;
  error?: string;
};

type TGenerationResult = {
  html: string;
  text: string;
};
```

