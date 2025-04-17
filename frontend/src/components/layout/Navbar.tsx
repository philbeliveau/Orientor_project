import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';

const Navbar = () => {
  const pathname = usePathname();

  const navItems = [
    { href: '/home', label: 'Home' },
    { href: '/space', label: 'Space' },
    { href: '/chat', label: 'Chat' },
    { href: '/profile', label: 'Profile' },
  ];

  return (
    <header className="fixed top-0 left-0 w-full z-50 bg-white/10 backdrop-blur-md px-6 py-4 flex justify-between items-center shadow-sm">
      <motion.div 
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="text-xl font-semibold tracking-tight text-gray-800"
      >
        Orientor
      </motion.div>
      
      <nav className="flex gap-6 text-sm uppercase">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`hover:text-blue-500 transition-colors duration-200 ${
              pathname === item.href ? 'text-blue-500' : 'text-gray-600'
            }`}
          >
            {item.label}
          </Link>
        ))}
      </nav>

      <motion.div 
        whileHover={{ scale: 1.05 }}
        className="w-8 h-8 bg-gradient-to-br from-blue-100 to-blue-200 rounded-full cursor-pointer"
      />
    </header>
  );
};

export default Navbar; 