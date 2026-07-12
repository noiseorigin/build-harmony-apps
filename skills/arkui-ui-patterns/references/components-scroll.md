# Scroll containers and list operations

Pattern quick-reference, checked 2026-07. Verify current signatures with `devecocli docs search <component>` when installed, or current Huawei docs.

## LazyForEach + IDataSource (long lists)

```ts
class MyDataSource implements IDataSource {
  private data: Item[] = [];
  totalCount(): number { return this.data.length; }
  getData(index: number): Item { return this.data[index]; }
  registerDataChangeListener(l: DataChangeListener): void { /* store */ }
  unregisterDataChangeListener(l: DataChangeListener): void { /* remove */ }
}

List() {
  LazyForEach(this.dataSource, (item: Item) => {
    ListItem() { ItemRow({ item }) }
  }, (item: Item) => item.id)      // key MUST be unique and stable
}
.cachedCount(5)
```

Mutations must go through the data source and fire the listener (`onDataAdd`/`onDataDelete`/...), not through a raw array.

## @Reusable rows

```ts
@Reusable @Component
struct MyRow {
  @State msg: Message = new Message('');
  aboutToReuse(params: Record<string, ESObject>) { this.msg = params.msg as Message; }
  aboutToRecycle() { /* release heavy resources */ }
  build() { Text(this.msg.value) }
}
```

Rules: reuse works within the same parent only; never nest `@Reusable` in `@Reusable`; combine with `LazyForEach`. Officially cited ~69% faster row creation.

## onVisibleAreaChange

```ts
Image(item.url).onVisibleAreaChange([0.0, 1.0], (visible: boolean, ratio: number) => {
  if (visible && ratio >= 1.0) { this.loadHighRes(); }
  if (!visible) { this.releaseImage(); }
})
```

Use for lazy media loading, video autoplay/pause, exposure analytics.

## Swiper (carousel)

```ts
Swiper() { ForEach(this.banners, (b: Banner) => Image(b.url).borderRadius(12)) }
.loop(true).autoPlay(true).interval(3000)
.indicator(new DotIndicator().selectedColor('#007DFF').itemWidth(8).selectedItemWidth(16))
```

## WaterFlow (waterfall)

```ts
WaterFlow({ scroller: this.scroller }) {
  LazyForEach(this.ds, (item: Card) => { FlowItem() { CardView({ item }) } }, (i: Card) => i.id)
}
.columnsTemplate('1fr 1fr').columnsGap(8).rowsGap(8).cachedCount(10)
```

## Grid

```ts
Grid() { ForEach(this.items, (i: Cell) => { GridItem() { CellView({ i }) } }) }
.columnsTemplate('1fr 1fr 1fr 1fr').rowsGap(12).columnsGap(12)
```

## Common list operations

- **Swipe-to-delete**: `ListItem().swipeAction({ end: { builder: deleteButtonBuilder, actionAreaDistance: 56 }, edgeEffect: SwipeEdgeEffect.Spring })`; splice inside `animateTo` for smooth removal.
- **Drag reorder**: `List().onItemDragStart(...)` + `.onItemDragMove(...)` splicing in `animateTo`.
- **Pull-to-refresh**: `Refresh({ refreshing: $$this.isRefreshing }) { List() {...} }.onRefreshing(...)`.
- **Load more**: `.onReachEnd(() => { if (!this.isLoading) loadNextPage(); })` — guard against duplicate triggers.
- **Scroll control**: `const scroller = new Scroller(); List({ scroller })`; `scroller.scrollEdge(Edge.Bottom)` / `scrollToIndex(n)` for chat-style behavior.
- **Keep position on prepend**: `.maintainVisibleContentPosition(true)` with LazyForEach.
- **Grouped + sticky headers**: `ListItemGroup({ header: this.sectionHeader(title) })` inside `List().sticky(StickyStyle.Header)`.

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT), derived from official ArkUI docs and best practices.
