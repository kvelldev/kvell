
# Design Tokens Rules

スタイリングにおいて、ハードコードされた値（Hex color, px sizing）の使用を禁止します。
必ず `src/styles/tokens.ts` (または `theme.ts`) で定義されたトークンを使用してください。

## Few-shot Example

### Bad (Hardcoded):
```tsx
<button style={{ backgroundColor: "#FF5733", padding: "10px" }}>
  Submit
</button>
````

### Good (Using Tokens):

```tsx
import { tokens } from '@/styles/tokens';

const Button = styled.button`
  background-color: ${tokens.color.primary.main};
  padding: ${tokens.spacing.md};
  border-radius: ${tokens.radius.sm};
  font-size: ${tokens.typography.size.body};
`;
```

