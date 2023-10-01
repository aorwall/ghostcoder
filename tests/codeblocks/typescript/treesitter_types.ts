// Importing modules
import { myFunction as func } from './myModule';
import myDefault, { myFunction } from './myModule';
import * as myModule from './myModule';
import myModule = require('myModule');

// Exporting modules
export { myFunction };
export * from './myModule';

// Enum declaration and assignment
enum MyEnum {
  Value1 = 1,
  Value2 = 2
}

// Interface declaration and extension
interface IMyBaseInterface { }
interface IMyDerivedInterface extends IMyBaseInterface { }

// Class declaration, extension, and implementation
abstract class MyBaseClass {
  abstract myAbstractMethod(input: string): void;
}

class MyDerivedClass extends MyBaseClass implements IMyInterface {
  public myField: string;
  override myAbstractMethod(input: string): void { }
  myMethod(arg: string): number { return 0; }
}

// Function declaration and usage
function myFunction(param1: string, param2: number) { }
let myVariable: typeof myFunction;

// Variable declaration and usage
let x = 10;
x += 5;
let y = x;
let z = 'Hello';
let a = 1 + 2;
let myNullableVar: number | null = null;
let myVar = myNullableVar!;
let myVariable: number = 10;

// Type declaration and usage
type MyType = string | number;
let myVariable: MyType;

// Try-catch block
try {
  // some code
} catch (error) {
  console.error(error);
}

// Console log
console.log("Hello, World!");

// New expression
let date = new Date();

// Other expressions
let x = (1 + 2) * 3;
let myInstance = new MyClass();
let myVariable = <number>someValue;
let myVariable = someValue as number;
let myVariable: number | undefined;
function myFunction(...restParams: number[]) { }
let myVariable: Array<number>;
function isString(test: any): test is string {
  return typeof test === "string";
}
let myVariable: typeof someOtherVariable;
type MyLookupType = MyClass['myProperty'];
type MyLiteralType = 'literal';
let myVariable: number;
let myVariable: string;
let myVariable: { property: string };
let myVariable: number[];
let myVariable: [number, string];
let myVariable: readonly number[];
let myVariable: number | string;
let myVariable: (param: string) => number;