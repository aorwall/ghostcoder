// 1. Variable Declarations
let number = 10;
const PI = 3.14;
var oldSchoolVariable = 'This is old style';

// 2. Function Declaration
function greet(name) {
  return `Hello, ${name}!`;
}

// 3. Arrow Function
const square = (x) => x * x;

// 4. Class Declaration
class Person {
  constructor(name, age) {
    this.name = name;
    this.age = age;
  }

  introduce() {
    return `Hi, I'm ${this.name} and I'm ${this.age} years old.`;
  }
}

// 5. Object Literal
const obj = {
  key: 'value',
  method() {
    return 'This is a method';
  }
};

// 6. Array Declaration
const array = [1, 2, 3, 4];

// 7. Loops
for (let i = 0; i < array.length; i++) {
  console.log(array[i]);
}

array.forEach((element) => {
  console.log(element);
});

// 8. Conditional
if (number > 5) {
  console.log('Number is greater than 5');
} else {
  console.log('Number is 5 or smaller');
}

// 9. Switch-case
switch (number) {
  case 10:
    console.log('Number is 10');
    break;
  default:
    console.log('Number is not 10');
    break;
}

// 10. Try-catch
try {
  throw new Error('This is an error');
} catch (error) {
  console.error('Caught an error:', error.message);
}


// 12. Destructuring
const { key } = obj;
const [firstElement] = array;

// 13. Spread/Rest
const newObj = { ...obj, newKey: 'newValue' };
const newArray = [...array, 5];

// 14. Template Literals
const message = `This is a number: ${number}`;

// 15. Import/Export (common in modules)
export { greet };
import { greet } from './path-to-this-file';

console.log('Demonstration complete.');