const asyncFunction = async () => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      resolve('Async function resolved');
    }, 1000);
  });
};

asyncFunction().then(console.log).catch(console.error);