/* Decap supplies createClass and h for preview components. */
CMS.registerPreviewStyle('/journal/ai-readable.css');
CMS.registerPreviewStyle('/site.css');
CMS.registerPreviewTemplate('articles', createClass({
  render: function () {
    const data = this.props.entry.get('data').toJS();
    const photo = (b, key) => {
      const asset = b.src ? this.props.getAsset(b.src) : null;
      return h('figure', {key, className: 'case-media'},
        asset ? h('img', {src: asset.toString(), alt: b.alt || '', style: {width: '100%', height: 'auto'}}) : h('p', {}, '사진을 선택해 주세요.'),
        b.caption ? h('figcaption', {}, b.caption) : null);
    };
    return h('article', {style: {maxWidth: '760px', margin: 'auto', padding: '24px', color: '#20252c', background: '#fff', lineHeight: '1.9'}},
      h('h1', {}, data.title || ''),
      h('aside', {className: 'answer-box'}, h('p', {}, data.summary || '')),
      h('div', {className: 'body'}, (data.blocks || []).map((b, i) => {
        if (b.type === 'image') return photo(b, i);
        if (b.type === 'sequence') return h('div', {key: i, className: 'clinical-sequence-grid'}, (b.images || []).map(photo));
        return h(b.type === 'heading' ? 'h2' : 'p', {key: i}, b.text || '');
      })));
  }
}));
