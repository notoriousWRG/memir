import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  integrations: [
    starlight({
      title: 'Memir',
      description: 'Lore system for homebrew D&D.',
      sidebar: [
        {
          label: 'Canon',
          autogenerate: { directory: 'canon' },
        },
        {
          label: 'Stories',
          autogenerate: { directory: 'stories' },
        },
        {
          label: 'Campaigns',
          autogenerate: { directory: 'campaigns' },
        },
      ],
    }),
  ],
});
