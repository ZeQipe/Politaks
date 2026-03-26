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
    taskId: string;  // конкретный id ассистента или "_all"
    modelId: string; // только конкретный id модели, "_all" недопустим
  };
  excelLink: string;
  range: {
    from: number; // >= 3
    to: number;   // 0 = весь документ, или >= 3
  };
};
```

**Примечания:**
- Используется для генерации контента из Excel файла
- `taskId: "_all"` — запуск фоновой обработки для всех ассистентов с поддержкой Excel (все записи `Assistant` с `key_title` из `ASSISTANT_METHODS`). Для каждого ассистента стартует свой поток с индивидуальным `sheet_id`.
- `modelId` должен быть конкретным id модели; значение `"_all"` возвращает ошибку 400.
- Поле `excelLink` содержит ссылку на Google Sheets / Excel файл
- `range.from` >= 3, `range.to` = 0 (весь документ) или >= 3
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

