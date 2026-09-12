import js from '@eslint/js';
import ts from 'typescript-eslint';
export default ts.config(
  {ignores:['dist/**','node_modules/**','playwright-report/**','test-results/**','src/Legacy*','src/legacyTypes.ts','src/types.ts']},
  js.configs.recommended,...ts.configs.recommended,
  {files:['**/*.{ts,tsx,js,mjs}'],languageOptions:{globals:{console:'readonly',process:'readonly',URL:'readonly',setTimeout:'readonly',fetch:'readonly'}},rules:{'@typescript-eslint/no-unused-vars':['error',{argsIgnorePattern:'^_',varsIgnorePattern:'^_'}],'@typescript-eslint/no-explicit-any':'off','no-undef':'off'}}
);
