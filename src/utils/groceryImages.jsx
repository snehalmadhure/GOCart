const catalog = '/images/groceries/catalog.png'

const grid = {
  bread: [0, 0], milk: [1, 0], eggs: [2, 0], banana: [3, 0],
  coffee: [0, 1], rice: [1, 1], pasta: [2, 1], tomato: [3, 1],
  onion: [0, 2], garlic: [1, 2], cheese: [2, 2], oil: [3, 2],
  butter: [0, 3], yogurt: [1, 3], flour: [2, 3], fallback: [3, 3],
}

export function getGroceryImage(itemName = '') {
  const name = itemName.toLowerCase().replace(/[^a-z]/g, '')
  const key = Object.keys(grid).find(candidate => name.includes(candidate)) || 'fallback'
  const [x, y] = grid[key]
  return { src: catalog, position: `${x * 33.333}% ${y * 33.333}%`, key }
}

export function GroceryImage({ name, className = '', decorative = false }) {
  const image = getGroceryImage(name)
  return <span role={decorative ? undefined : 'img'} aria-label={decorative ? undefined : `${name} product image`} aria-hidden={decorative || undefined} className={`block shrink-0 bg-[#fbf8f0] bg-no-repeat ${className}`} style={{ backgroundImage: `url(${image.src})`, backgroundSize: '400% 400%', backgroundPosition: image.position }} />
}
