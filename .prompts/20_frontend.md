
# Frontend Architecture Rules (React + Atomic Design)

## Atomic Design Classification
迷った場合は以下の基準で配置すること。

- **Atoms**: 最小単位（Button, Icon, Label）。ロジックを持たない。
- **Molecules**: Atomsの組み合わせ（InputForm, SearchBar）。ドメイン知識を持たない。
- **Organisms**: 特定のドメイン知識を持つ独立したUI部品（Header, UserCard）。
- **Templates**: レイアウト構造。
- **Pages**: ルーティングに対応するページ。データフェッチのトリガーを持つ。

## Separation of Concern (Logic vs View)
Clean Architectureの思想に基づき、View（Component）にビジネスロジックを書かないこと。

### Example: Custom Hook Pattern
**Bad:** Component内で直接fetchする
```tsx
export const UserProfile = () => {
  const [user, setUser] = useState(null);
  useEffect(() => { fetch... }, []); // No!
  return <div>{user.name}</div>;
}
```

**Good:** UseCase(Hook)に切り出す

```tsx
// features/user/hooks/useUser.ts (UseCase Layer)
export const useUser = (userId: string) => {
  // Fetching logic here
  return { user, isLoading, error };
}

// features/user/components/UserProfile.tsx (View Layer)
export const UserProfile = ({ userId }) => {
  const { user, isLoading } = useUser(userId); // Use the hook
  if (isLoading) return <Loading />;
  return <div>{user.name}</div>;
}
```

