export default {
  name: 'product',
  title: 'المنتجات',
  type: 'document',
  fields: [
    {
      name: 'title',
      title: 'اسم المنتج',
      type: 'string',
    },
    {
      name: 'slogan',
      title: 'السلوجن / الوصف المختصر (مثل: عطر من الخيال)',
      type: 'string',
    },
    {
      name: 'description',
      title: 'وصف المنتج وتفاصيله الكاملة',
      type: 'text',
    },
    {
      name: 'image',
      title: 'صورة المنتج الأساسية',
      type: 'image',
      options: {
        hotspot: true,
      },
    },
    {
      name: 'sizes',
      title: 'الأحجام والأسعار المتوفرة',
      type: 'array',
      of: [
        {
          type: 'object',
          name: 'sizeVariant',
          title: 'حجم المنتج',
          fields: [
            {
              name: 'size',
              title: 'الحجم أو السعة (مثلاً: 30ml أو 50ml)',
              type: 'string',
            },
            {
              name: 'price',
              title: 'السعر الحالي / بعد الخصم (ج.م)',
              type: 'number',
            },
            {
              name: 'originalPrice',
              title: 'السعر قبل الخصم (ج.م) - اختياري',
              type: 'number',
            },
            {
              name: 'inStock',
              title: 'متوفر في المخزون؟',
              type: 'boolean',
              initialValue: true,
            },
            {
              name: 'quantity',
              title: 'الكمية المتوفرة من الحجم ده',
              type: 'number',
              initialValue: 1,
            },
          ],
        },
      ],
    },
  ],
}