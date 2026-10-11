export function Metrics({ items }: { items: { label: string; value: string; detail?: string }[] }) {
  return <dl className="metrics">{items.map((item) => <div key={item.label}><dt>{item.label}</dt><dd>{item.value}</dd>{item.detail && <small>{item.detail}</small>}</div>)}</dl>;
}

