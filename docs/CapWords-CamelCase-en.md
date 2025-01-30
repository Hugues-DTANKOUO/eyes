# CapWords & CamelCase

CapWords and CamelCase are two naming conventions used in programming to name elements like classes, methods, variables, etc. They help make names more readable by indicating word boundaries without using spaces. Here's an explanation of each:

## CapWords

Also known as *PascalCase*, this convention starts each word with a capital letter and joins them without spaces. It's frequently used for naming classes in many programming languages, including Python. For example, `ClassName` is an identifier written in CapWords. [PEP 8](PEP8-summary.md) recommends using `CapWords` for class names in Python. We will follow this convention in this project.

## CamelCase

`CamelCase` is similar to `CapWords`, but the difference lies in the initial letter of the first word: in `CamelCase`, the first letter is lowercase, while in `CapWords`, it's uppercase. `CamelCase` is often used for naming methods or variables in some programming languages. For example, `variableName` or `calculationMethod` are identifiers written in `CamelCase`. However, in Python, the [PEP 8](PEP8-summary.md) convention recommends using `snake_case` (`variable_name`, `calculation_method`) for functions, methods, and variables rather than `CamelCase`.

---

In summary, `CapWords` (or `PascalCase`) starts each word with a capital letter and is used for class names in Python, according to [PEP 8](PEP8-summary.md). CamelCase starts the first word with a lowercase letter and is less frequently used in Python for function and variable names, as [PEP 8](PEP8-summary.md) recommends using `snake_case` for these elements instead.