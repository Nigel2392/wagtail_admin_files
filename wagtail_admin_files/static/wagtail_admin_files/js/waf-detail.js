class Clipboard extends window.StimulusModule.Controller {
  // declare readonly hasButtonTarget: boolean
  // declare originalContent: string
  // declare successDurationValue: number
  // declare successContentValue: string
  // declare timeout: number
  // declare readonly buttonTarget: HTMLElement
  // declare readonly sourceTarget: HTMLInputElement

  static targets = ["button", "source"]
  static values = {
    successContent: String,
    successDuration: {
      type: Number,
      default: 2000,
    },
  }

  connect() {
    if (!this.hasButtonTarget) return

    this.originalContent = this.buttonTarget.innerHTML
  }

  copy(event) {
    event.preventDefault()

    const text = this.sourceTarget.innerHTML || this.sourceTarget.value

    navigator.clipboard.writeText(text).then(() => this.copied())
  }

  copied() {
    if (!this.hasButtonTarget) return

    if (this.timeout) {
      clearTimeout(this.timeout)
    }

    this.buttonTarget.innerHTML = this.successContentValue

    // @ts-expect-error
    this.timeout = setTimeout(() => {
      this.buttonTarget.innerHTML = this.originalContent
    }, this.successDurationValue)
  }
}

window.wagtail.app.register("waf-clipboard", Clipboard)