@Entry
@Component
struct Index {
  @State private status: string = 'Ready';

  build() {
    Column({ space: 16 }) {
      Text($r('app.string.page_title'))
        .fontSize($r('app.float.page_title_size'))
        .fontWeight(FontWeight.Bold)

      Text(this.status)

      Button($r('app.string.continue_button'))
        .onClick(() => {
          this.status = 'Running';
        })
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
    .padding($r('app.float.page_padding'))
  }
}
