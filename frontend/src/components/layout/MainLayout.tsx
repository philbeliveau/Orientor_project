// 'use client';
// import { useEffect, useState } from 'react';
// import Link from 'next/link';
// import { useRouter } from 'next/navigation';

// export default function MainLayout({ children }: { children: React.ReactNode }) {
//     const [isLoggedIn, setIsLoggedIn] = useState(false);
//     const router = useRouter();

//     useEffect(() => {
//         // Check if user is logged in
//         const token = localStorage.getItem('access_token');
//         setIsLoggedIn(!!token);
//     }, []);

//     const handleLogout = () => {
//         localStorage.removeItem('access_token');
//         setIsLoggedIn(false);
//         router.push('/login');
//     };

//     return (
//         <div className="min-h-screen bg-gray-900">
//             <nav className="bg-gray-800 border-b border-gray-700">
//                 <div className="max-w-7xl mx-auto px-4">
//                     <div className="flex justify-between h-16">
//                         <div className="flex items-center">
//                             <h1 className="text-xl font-bold text-blue-400">Orientor</h1>
//                         </div>
//                         <div className="flex items-center space-x-4">
//                             {isLoggedIn ? (
//                                 <>
//                                     <Link href="/profile" className="text-gray-300 hover:text-white">
//                                         Profile
//                                     </Link>
//                                     <button
//                                         onClick={handleLogout}
//                                         className="text-gray-300 hover:text-white"
//                                     >
//                                         Logout
//                                     </button>
//                                 </>
//                             ) : (
//                                 <>
//                                     <Link href="/login" className="text-gray-300 hover:text-white">
//                                         Login
//                                     </Link>
//                                     <Link href="/register" className="text-gray-300 hover:text-white">
//                                         Register
//                                     </Link>
//                                 </>
//                             )}
//                         </div>
//                     </div>
//                 </div>
//             </nav>
//             <main className="max-w-7xl mx-auto px-4 py-6">
//                 {children}
//             </main>
//         </div>
//     );
// }
export default function MainLayout({ children }: { children: React.ReactNode }) {
    return (
      <div className="min-h-screen bg-white">
        <nav className="bg-gray-100 border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-bold text-blue-600">Orientor</h1>
              </div>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 py-6">
          {children}
        </main>
      </div>
    );
  }