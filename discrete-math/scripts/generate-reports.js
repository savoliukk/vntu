const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const readJson = (rel) => JSON.parse(fs.readFileSync(path.join(root, rel), "utf8"));

const pr1 = readJson("practice-01/artifacts/pr1_tasks1_3_results.json");
const pr2 = readJson("practice-02/artifacts/pr2_tasks4_6_results.json");
const pr3 = readJson("practice-03/artifacts/pr3_tasks7_9_results.json");

function titlePage(number, subtitle, variants) {
  return `<div align="center">

# Вінницький національний технічний університет

Факультет інтелектуальних інформаційних технологій та автоматизації

<br><br><br><br><br><br><br><br>

## Звіт до практичної роботи №${number}

**«${subtitle}»**

<br><br>

**Курс:** 1  
**Група:** 4КН-25б  
**Варіанти задач:** ${variants}  

</div>

<br><br><br><br><br>

<div align="right">

**Виконав:** Саволюк Микола Миколайович  

**Викладач:** Шевчук Олександр Федорович

</div>

<br><br>

<div align="center">

**Рік:** 2026

</div>

<div style="page-break-after: always;"></div>
`;
}

function setFmt(items) {
  return `{${items.join(", ")}}`;
}

function boolTable(rows, columns) {
  const mdCell = (value) => String(value).replace(/\|/g, "\\|");
  const header = `| ${columns.map((c) => mdCell(c.label)).join(" | ")} |`;
  const sep = `| ${columns.map(() => "---").join(" | ")} |`;
  const body = rows.map((row) => `| ${columns.map((c) => mdCell(row[c.key])).join(" | ")} |`);
  return [header, sep, ...body].join("\n");
}

function matrixTable(labels, matrix) {
  const header = `| R | ${labels.join(" | ")} |`;
  const sep = `| --- | ${labels.map(() => "---").join(" | ")} |`;
  const body = matrix.map((row, i) => `| ${labels[i]} | ${row.join(" | ")} |`);
  return [header, sep, ...body].join("\n");
}

function coverageTable(rows) {
  const labels = Object.keys(rows);
  const header = "| Рядок | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | a |";
  const sep = "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |";
  const body = labels.map((name) => {
    const row = rows[name];
    const cells = Array.from({ length: 9 }, (_, i) => row.items.includes(i + 1) ? "1" : "");
    return `| ${name} | ${cells.join(" | ")} | ${row.cost} |`;
  });
  return [header, sep, ...body].join("\n");
}

function relationPairs(pairs) {
  return pairs.map(([a, b]) => `(${a}, ${b})`).join(", ");
}

function mermaidRelation(task) {
  const lines = ["graph LR"];
  for (const x of task.D) lines.push(`  v${x}(("${x}"))`);
  for (const [a, b] of task.relation) lines.push(`  v${a} --> v${b}`);
  return lines.join("\n");
}

function karnaughTable(kmap) {
  const rows = ["00", "01", "11", "10"];
  const cols = ["00", "01", "11", "10"];
  const header = "| AB \\ CD | " + cols.join(" | ") + " |";
  const sep = "| --- | --- | --- | --- | --- |";
  const body = kmap.map((row, i) => `| ${rows[i]} | ${row.join(" | ")} |`);
  return [header, sep, ...body].join("\n");
}

function quineStageTable(stage) {
  return [
    "| Імпліканта | Покриває мінтерми |",
    "| --- | --- |",
    ...stage.map((item) => `| ${item.pattern} | ${item.terms.join(", ")} |`),
  ].join("\n");
}

function quineChart(task) {
  const header = `| Імпліканта | ${task.minterms.join(" | ")} |`;
  const sep = `| --- | ${task.minterms.map(() => "---").join(" | ")} |`;
  const body = task.primeImplicants.map((p) => {
    const marks = task.minterms.map((m) => task.chart[m].includes(p.pattern) ? "×" : "");
    return `| ${p.pattern} | ${marks.join(" | ")} |`;
  });
  return [header, sep, ...body].join("\n");
}

function pr1Report() {
  return `${titlePage(1, "Множини та діаграми Венна", "Задача 1: №29; Задача 2: №19; Задача 3: №43, №6")}

## Мета роботи

Набути навичок виконання операцій над множинами, подання заданих множин через базові множини, а також запису зафарбованих областей діаграм Венна мовою операцій над множинами.

## Короткі теоретичні відомості

У роботі використовуються такі операції над множинами:

| Операція | Зміст |
| --- | --- |
| A ∪ B | об'єднання множин |
| A ∩ B | перетин множин |
| A \\ B | різниця множин |
| Ā | доповнення множини A до універсальної множини U |

---

## Задача 1. Варіант №29

За умовою задано:

U = ${setFmt(pr1.task1.U)}  
A = ${setFmt(pr1.task1.A)}  
B = ${setFmt(pr1.task1.B)}  
C = ${setFmt(pr1.task1.C)}  
D = ${setFmt(pr1.task1.D)}

Потрібно обчислити множину:

X = (A ∪ B) ∪ (C̄ ∩ D̄)

### Покрокове виконання

1. Знаходжу об'єднання множин A і B:

A ∪ B = ${setFmt(pr1.task1.aUnionB)}

2. Знаходжу доповнення множини C:

C̄ = U \\ C = ${setFmt(pr1.task1.notC)}

3. Знаходжу доповнення множини D:

D̄ = U \\ D = ${setFmt(pr1.task1.notD)}

4. Знаходжу перетин доповнень:

C̄ ∩ D̄ = ${setFmt(pr1.task1.notCAndNotD)}

5. Остаточно:

X = ${setFmt(pr1.task1.aUnionB)} ∪ ${setFmt(pr1.task1.notCAndNotD)}

X = ${setFmt(pr1.task1.result)}

Відповідь:

**X = ${setFmt(pr1.task1.result)}**

---

## Задача 2. Варіант №19

Задано універсальну множину та множини:

U = ${setFmt([1, 2, 3, 4, 5, 6, 7, 8, 9])}  
A = ${setFmt([1, 2, 3, 4, 5, 9])}  
B = ${setFmt([2, 4, 6, 8])}  
C = ${setFmt([1, 3, 5, 7])}  
D = ${setFmt([1, 4, 5, 7, 8, 9])}

Для варіанта №19 потрібно подати через A, B, C, D множину:

M = ${setFmt(pr1.task2.target)}

Обираю подання:

M = (B ∪ D) ∪ (A \\ C)

### Перевірка подання

1. Знаходжу об'єднання B і D:

B ∪ D = ${setFmt(pr1.task2.bUnionD)}

2. Знаходжу різницю A \\ C:

A \\ C = ${setFmt(pr1.task2.aMinusC)}

3. Об'єдную отримані множини:

(B ∪ D) ∪ (A \\ C) = ${setFmt(pr1.task2.bUnionD)} ∪ ${setFmt(pr1.task2.aMinusC)}

(B ∪ D) ∪ (A \\ C) = ${setFmt(pr1.task2.result)}

Отримана множина збігається із заданою множиною M, отже:

**M = (B ∪ D) ∪ (A \\ C)**

---

## Задача 3. Варіанти №43, №6

Потрібно за діаграмами Венна записати зафарбовані області через множини A, B, C, D.

### Варіант №43

![Діаграма Венна для варіанта 43](artifacts/venn_variant43.jpg)

На діаграмі зафарбовано всю область множини C, а також частину, що належить одночасно A і B. Тому:

**E₄₃ = C ∪ (A ∩ B)**

### Варіант №6

![Діаграма Венна для варіанта 6](artifacts/venn_variant6.jpg)

Зафарбована горизонтальна смуга лежить у спільній частині всіх чотирьох множин A, B, C і D. Тому:

**E₆ = A ∩ B ∩ C ∩ D**

---

## Перевірка результатів

Контрольні обчислення виконано скриптом:

\`artifacts/solve_pr1_tasks1_3.js\`

Файл результатів:

\`artifacts/pr1_tasks1_3_results.json\`

Скрипт підтвердив:

| Задача | Контрольний результат |
| --- | --- |
| 1 | X = ${setFmt(pr1.task1.result)} |
| 2 | M = ${setFmt(pr1.task2.result)} |
| 3, №43 | E₄₃ = C ∪ (A ∩ B) |
| 3, №6 | E₆ = A ∩ B ∩ C ∩ D |

## Висновок

У практичній роботі №1 виконано три задачі з різними варіантами. Для задачі 1 обчислено результат операцій над множинами, для задачі 2 задану множину подано через A, B, C, D, а для задачі 3 за двома діаграмами Венна записано відповідні області через операції над множинами.
`;
}

function pr2Report() {
  return `${titlePage(2, "Бінарні відношення, покриття та комбінаторика", "Задача 4: №9; Задача 5: №24; Задача 6: №59, №33")}

## Мета роботи

Навчитися будувати бінарні відношення за предикатом, подавати їх списком пар, матрицею та графом, знаходити мінімальні й найкоротші покриття, а також застосовувати базові правила комбінаторики.

---

## Задача 4. Варіант №9

Задано множину:

D = ${setFmt(pr2.task4.D)}

Відношення R ⊆ D × D задано предикатом:

(m, n) ∈ R ⇔ (3m + 1 - 2n) є парним числом.

### Спрощення предиката

Розглядаю парність виразу:

3m + 1 - 2n ≡ m + 1 (mod 2),

оскільки 3m має ту саму парність, що й m, а 2n завжди парне. Отже, вираз є парним тоді й лише тоді, коли m + 1 парне, тобто m непарне.

Тому до R входять усі пари, у яких перша координата m ∈ {1, 3, 5}, а друга координата n може бути будь-яким елементом D.

R = {${relationPairs(pr2.task4.relation)}}

### Матричне подання

${matrixTable(pr2.task4.D, pr2.task4.matrix)}

### Графічне подання

\`\`\`mermaid
${mermaidRelation(pr2.task4)}
\`\`\`

### Класифікація відношення

| Властивість | Висновок | Пояснення |
| --- | --- | --- |
| Рефлексивність | ні | відсутні пари (2, 2), (4, 4), (6, 6) |
| Антирефлексивність | ні | наявні пари (1, 1), (3, 3), (5, 5) |
| Симетричність | ні | (1, 2) ∈ R, але (2, 1) ∉ R |
| Антисиметричність | ні | (1, 3) ∈ R і (3, 1) ∈ R, хоча 1 ≠ 3 |
| Асиметричність | ні | є петлі та взаємні пари |
| Транзитивність | так | якщо друга координата проміжної пари парна, наступної пари з неї немає; якщо непарна, то початковий непарний m вже пов'язаний з усіма елементами D |

---

## Задача 5. Варіант №24

Для таблиці покриттів B24 потрібно побудувати мінімальне та найкоротше покриття.

![Фрагмент таблиці покриттів B24](artifacts/B24_crop.png)

${coverageTable(pr2.task5.rows)}

У вигляді множин рядки мають вигляд:

| Рядок | Множина | Ціна |
| --- | --- | --- |
${Object.entries(pr2.task5.rows).map(([name, row]) => `| ${name} | ${setFmt(row.items)} | ${row.cost} |`).join("\n")}

### Мінімальне покриття

Перевіряю покриття з найменшою сумарною ціною. Рядки B, F, G, H мають ціну 1 кожен:

B = ${setFmt(pr2.task5.rows.B.items)}  
F = ${setFmt(pr2.task5.rows.F.items)}  
G = ${setFmt(pr2.task5.rows.G.items)}  
H = ${setFmt(pr2.task5.rows.H.items)}

Їх об'єднання:

B ∪ F ∪ G ∪ H = ${setFmt([1, 2, 3, 4, 5, 6, 7, 8, 9])}

Сумарна ціна:

a(B) + a(F) + a(G) + a(H) = 1 + 1 + 1 + 1 = 4.

Покриття з ціною 3 неможливе: якщо взяти B для покриття стовпця 2 і H для стовпця 7, то ще залишаються елементи 1, 4, 5, 6, які одним рядком ціни 1 не покриваються; якщо замість B брати A, то вже витрачається ціна 3 і все одно лишаються непокриті елементи.

Отже, мінімальне покриття:

**B ∪ F ∪ G ∪ H**, сумарна ціна **4**.

### Найкоротше покриття

Найкоротше покриття має мінімальну кількість рядків. Один рядок не покриває всі 9 елементів, тому перевіряю пари рядків.

A = ${setFmt(pr2.task5.rows.A.items)}  
E = ${setFmt(pr2.task5.rows.E.items)}

A ∪ E = ${setFmt(pr2.task5.rows.A.items)} ∪ ${setFmt(pr2.task5.rows.E.items)} = ${setFmt([1, 2, 3, 4, 5, 6, 7, 8, 9])}

Отже, найкоротше покриття:

**A ∪ E**, кількість рядків **2**, сумарна ціна **6**.

---

## Задача 6. Варіанти №59, №33

### Варіант №59

Потрібно порахувати кількість способів розмістити 9 різних пасажирів у трьох різних вагонах.

1. Без додаткових обмежень кожен пасажир має 3 варіанти вибору вагона:

3⁹ = ${pr2.task6.variant59.allPlacements}

2. Якщо у перший вагон сідають рівно 3 пасажири, спочатку вибираю цих пасажирів, а решта 6 розподіляються між двома вагонами:

C(9, 3) · 2⁶ = 84 · 64 = ${pr2.task6.variant59.firstCarExactly3}

3. Якщо у кожний вагон сідають рівно 3 пасажири:

9! / (3! · 3! · 3!) = ${pr2.task6.variant59.eachCarExactly3}

4. Якщо в один вагон сідає 4 пасажири, у другий 3, у третій 2, то спочатку розподіляю пасажирів за групами, а потім враховую перестановку ролей трьох вагонів:

3! · 9! / (4! · 3! · 2!) = ${pr2.task6.variant59.distribution4_3_2}

### Варіант №33

Потрібно опустити 5 різних листів у 11 різних поштових скриньок так, щоб у кожній скриньці було не більше одного листа.

Для першого листа є 11 скриньок, для другого 10, далі 9, 8 і 7:

A(11, 5) = 11 · 10 · 9 · 8 · 7 = ${pr2.task6.variant33.lettersIntoBoxes}

---

## Перевірка результатів

Контрольні обчислення виконано скриптом:

\`artifacts/solve_pr2_tasks4_6.js\`

Файл результатів:

\`artifacts/pr2_tasks4_6_results.json\`

Скрипт підтвердив матрицю відношення, мінімальне покриття **BFGH**, найкоротше покриття **AE**, а також усі числові відповіді комбінаторних задач.

## Висновок

У практичній роботі №2 побудовано та класифіковано бінарне відношення, знайдено мінімальне й найкоротше покриття для таблиці B24, а також розв'язано дві комбінаторні задачі. Мінімальне покриття за ціною не збігається з найкоротшим: **BFGH** має меншу ціну, а **AE** має меншу кількість рядків.
`;
}

function pr3Report() {
  const task7Columns = [
    { key: "i", label: "i" },
    { key: "A", label: "A" },
    { key: "B", label: "B" },
    { key: "C", label: "C" },
    { key: "D", label: "D" },
    { key: "implication", label: "A→B" },
    { key: "bxord", label: "B⊕D" },
    { key: "right", label: "C∧(B⊕D)" },
    { key: "f", label: "f" },
  ];
  const task8Columns = [
    { key: "i", label: "i" },
    { key: "A", label: "A" },
    { key: "B", label: "B" },
    { key: "C", label: "C" },
    { key: "D", label: "D" },
    { key: "implication", label: "A→B" },
    { key: "sheffer", label: "C|B" },
    { key: "equivalence", label: "(A→B)~(C|B)" },
    { key: "f", label: "f" },
  ];

  return `${titlePage(3, "Логічні функції, карти Карно та метод Квайна", "Задача 7: №14; Задача 8: №1; Задача 9: №2")}

## Мета роботи

Навчитися складати таблиці істинності для логічних функцій, мінімізувати булеві функції за допомогою карт Карно у ДНФ та КНФ, а також виконувати мінімізацію методом Квайна.

## Умовні позначення

| Позначення | Зміст |
| --- | --- |
| ¬A | заперечення |
| A ∧ B | кон'юнкція |
| A ∨ B | диз'юнкція |
| A ⊕ B | виключне АБО |
| A ~ B | рівнозначність |
| A → B | імплікація |
| A \\| B | штрих Шеффера, тобто ¬(A ∧ B) |

---

## Задача 7. Варіант №14

Задана логічна функція:

f = (A → B) ~ (C ∧ (B ⊕ D))

### Покрокове обчислення

Для кожного набору значень A, B, C, D послідовно обчислюю:

1. A → B = ¬A ∨ B.
2. B ⊕ D.
3. C ∧ (B ⊕ D).
4. f як рівнозначність між результатами кроків 1 і 3.

Повна таблиця істинності:

${boolTable(pr3.task7.rows, task7Columns)}

Вектор значень функції:

f = [${pr3.task7.vector.join(", ")}]

---

## Задача 8. Варіант №1

Задана логічна функція:

f = ((A → B) ~ (C | B)) ⊕ D,

де C | B = ¬(C ∧ B).

### Таблиця істинності

${boolTable(pr3.task8.rows, task8Columns)}

Мінтерми функції:

F = Σ(${pr3.task8.minterms.join(", ")})

Нульові набори:

F₀ = (${pr3.task8.zeros.join(", ")})

### Карта Карно

Порядок рядків AB і стовпців CD взято у коді Ґрея: 00, 01, 11, 10.

${karnaughTable(pr3.task8.karnaugh)}

### Мінімізація у ДНФ

За картою Карно одиничні клітинки об'єднуються у такі пари:

| Група | Мінтерми | Імпліканта |
| --- | --- | --- |
| 1 | 4, 12 | B ∧ ¬C ∧ ¬D |
| 2 | 7, 15 | B ∧ C ∧ D |
| 3 | 0, 2 | ¬A ∧ ¬B ∧ ¬D |
| 4 | 9, 11 | A ∧ ¬B ∧ D |

Отже:

**мінДНФ:** f = ${pr3.task8.minDnf}

### Мінімізація у КНФ

Для КНФ групую нульові клітинки карти Карно. Отримано:

**мінКНФ:** f = ${pr3.task8.minCnf}

У мінДНФ маємо 4 кон'юнктивні члени по 3 літери, тобто 12 літер. У мінКНФ маємо 4 диз'юнктивні дужки по 3 літери, також 12 літер. За кількістю літер обидві форми мають однакову складність.

---

## Задача 9. Варіант №2

Задано функцію:

F = (${pr3.task9.minterms.join(", ")})

Потрібно мінімізувати її методом Квайна.

### Етап 1. Початкові терми

Записую мінтерми у двійковому коді:

${quineStageTable(pr3.task9.stages[0])}

### Етап 2. Склеювання термів

Склеюю пари термів, які відрізняються рівно одним бітом:

${quineStageTable(pr3.task9.stages[1])}

Після цього подальше склеювання неможливе, тому отримані імпліканти є первинними.

### Етап 3. Таблиця покриття первинними імплікантами

${quineChart(pr3.task9)}

Істотні імпліканти:

${pr3.task9.essential.join(", ")}

Імпліканта 0-01 покриває мінтерм 5, який не покривається жодною іншою первинною імплікантою. Імпліканта 111- покриває мінтерм 15, який також покривається лише нею.

Після вибору істотних імплікант залишаються мінтерми 2, 3, 10. Для їх покриття можна взяти імпліканти -010 і 00-1. Отримуємо мінімальне покриття:

${pr3.task9.selected.join(", ")}

### Мінімізована функція

Переводжу вибрані імпліканти у логічний вираз:

| Імпліканта | Вираз |
| --- | --- |
| -010 | ¬B ∧ C ∧ ¬D |
| 0-01 | ¬A ∧ ¬C ∧ D |
| 00-1 | ¬A ∧ ¬B ∧ D |
| 111- | A ∧ B ∧ C |

Отже:

**Fmin = ${pr3.task9.minDnf}**

---

## Перевірка результатів

Контрольні обчислення виконано скриптом:

\`artifacts/solve_pr3_tasks7_9.js\`

Файл результатів:

\`artifacts/pr3_tasks7_9_results.json\`

Скрипт сформував таблиці істинності, карту Карно, мінДНФ, мінКНФ і таблицю покриття для методу Квайна.

## Висновок

У практичній роботі №3 складено таблицю істинності для функції варіанта №14, мінімізовано функцію варіанта №1 за картою Карно та виконано мінімізацію функції варіанта №2 методом Квайна. Для задачі 8 мінДНФ і мінКНФ мають однакову складність, а для задачі 9 отримано мінімізовану ДНФ з чотирьох імплікант.
`;
}

const reports = [
  ["practice-01/report.md", pr1Report()],
  ["practice-02/report.md", pr2Report()],
  ["practice-03/report.md", pr3Report()],
];

for (const [name, content] of reports) {
  fs.writeFileSync(path.join(root, name), content, "utf8");
}

fs.writeFileSync(path.join(root, "practice-02", "artifacts", "B24_table.md"), coverageTable(pr2.task5.rows) + "\n", "utf8");
fs.writeFileSync(path.join(root, "practice-03", "artifacts", "task7_truth_table.md"), boolTable(pr3.task7.rows, [
  { key: "i", label: "i" },
  { key: "A", label: "A" },
  { key: "B", label: "B" },
  { key: "C", label: "C" },
  { key: "D", label: "D" },
  { key: "implication", label: "A→B" },
  { key: "bxord", label: "B⊕D" },
  { key: "right", label: "C∧(B⊕D)" },
  { key: "f", label: "f" },
]) + "\n", "utf8");
fs.writeFileSync(path.join(root, "practice-03", "artifacts", "task8_truth_table.md"), boolTable(pr3.task8.rows, [
  { key: "i", label: "i" },
  { key: "A", label: "A" },
  { key: "B", label: "B" },
  { key: "C", label: "C" },
  { key: "D", label: "D" },
  { key: "implication", label: "A→B" },
  { key: "sheffer", label: "C|B" },
  { key: "equivalence", label: "(A→B)~(C|B)" },
  { key: "f", label: "f" },
]) + "\n", "utf8");
fs.writeFileSync(path.join(root, "practice-03", "artifacts", "task9_quine_chart.md"), quineChart(pr3.task9) + "\n", "utf8");

console.log("Reports generated:");
for (const [name] of reports) console.log(path.join(root, name));
